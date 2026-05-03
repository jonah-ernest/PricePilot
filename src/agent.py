import re
import pandas as pd

from src.benchmarking import summarize_market
from src.simulation import simulate_revenue
from src.recommendation import recommend_price
from src.llm_reasoning import generate_business_explanation
from src.refresh_data import fetch_google_shopping_results
from src.prompt_parser import parse_pricing_prompt
from src.scraper import get_real_saas_pricing_data

def build_strategy_profile(parsed):
    return {
        "product_query": parsed.get("product_query"),
        "business_type": parsed.get("business_type"),
        "objective": parsed.get("objective", "maximize_revenue"),
        "audience": parsed.get("audience"),
        "positioning": parsed.get("positioning"),
        "key_features": parsed.get("key_features", []),
        "differentiation": parsed.get("differentiation"),
        "customer_problem": parsed.get("customer_problem"),
        "sales_channel": parsed.get("sales_channel"),
        "launch_stage": parsed.get("launch_stage"),
        "competitor_frame": parsed.get("competitor_frame"),
        "price_sensitivity": parsed.get("price_sensitivity"),
        "risk_tolerance": parsed.get("risk_tolerance"),
        "strategic_direction": parsed.get("strategic_direction"),
        "strategy_summary": parsed.get("strategy_summary"),
        "cost_floor": extract_cost_floor_from_text(parsed.get("raw_context", "")),
    }


def classify_market_position(price, market_summary):
    median_price = market_summary["median_price"]

    if price < median_price * 0.85:
        return "budget"
    if price <= median_price * 1.15:
        return "mid-market"
    return "premium"


def extract_cost_floor_from_text(text):
    text = text or ""
    lower = text.lower()

    constraint_words = [
        "cost",
        "cogs",
        "floor",
        "minimum",
        "min price",
        "less than",
        "below",
        "at least",
        "margin",
    ]

    if not any(word in lower for word in constraint_words):
        return None

    matches = re.findall(r"\$?\s*(\d+(?:\.\d+)?)", text)
    if not matches:
        return None

    values = [float(x) for x in matches]
    return max(values) if values else None


def estimate_price_row(simulation_df, price_value):
    """
    Create a synthetic simulation row when a guardrail price is outside
    the original simulated price range.

    This prevents the agent from recommending prices below a cost floor.
    """
    sim = simulation_df.sort_values("price").copy()

    if sim.empty:
        conversion_rate = 0.01
        expected_customers = 10
        expected_revenue = price_value * expected_customers

        return pd.Series(
            {
                "price": price_value,
                "conversion_rate": conversion_rate,
                "expected_customers": expected_customers,
                "expected_revenue": expected_revenue,
            }
        )

    # Estimate total available monthly visitors/customers implied by the model.
    valid_rows = sim[sim["conversion_rate"] > 0].copy()
    if valid_rows.empty:
        traffic_base = 1000
    else:
        traffic_base = float(
            (
                valid_rows["expected_customers"]
                / valid_rows["conversion_rate"]
            ).median()
        )

    max_price = float(sim["price"].max())
    min_conversion = float(sim["conversion_rate"].min())

    if price_value <= max_price:
        nearest_row = sim.iloc[(sim["price"] - price_value).abs().argsort()[:1]].iloc[0]
        conversion_rate = float(nearest_row["conversion_rate"])
    else:
        # Extrapolate demand downward when the required price is above
        # the original simulated range.
        price_ratio = max_price / price_value if price_value > 0 else 1
        conversion_rate = min_conversion * (price_ratio ** 1.5)

    # Avoid impossible zero-demand outputs while still penalizing high prices.
    conversion_rate = max(min(conversion_rate, 0.95), 0.001)

    expected_customers = traffic_base * conversion_rate
    expected_revenue = price_value * expected_customers

    return pd.Series(
        {
            "price": round(float(price_value), 2),
            "conversion_rate": round(float(conversion_rate), 4),
            "expected_customers": round(float(expected_customers), 0),
            "expected_revenue": round(float(expected_revenue), 2),
        }
    )


def select_guardrailed_price(simulation_df, market_summary, objective, positioning, floor_price):
    candidates = simulation_df.copy()
    median_price = float(market_summary["median_price"])

    minimum_allowed_price = 0

    if floor_price is not None:
        minimum_allowed_price = max(minimum_allowed_price, float(floor_price))

    if positioning == "premium" or objective == "premium_positioning":
        minimum_allowed_price = max(minimum_allowed_price, median_price * 1.05)

    # Hard rule: never recommend below the minimum allowed price.
    candidates = candidates[candidates["price"] >= minimum_allowed_price]

    if candidates.empty:
        synthetic_row = estimate_price_row(simulation_df, minimum_allowed_price)
        candidates = pd.DataFrame([synthetic_row])

    if objective == "maximize_growth":
        selected_row = candidates.loc[candidates["expected_customers"].idxmax()]

    elif objective == "competitive_entry":
        target_price = max(median_price * 0.9, minimum_allowed_price)
        selected_row = candidates.iloc[
            (candidates["price"] - target_price).abs().argsort()[:1]
        ].iloc[0]

    elif objective == "premium_positioning":
        selected_row = candidates.loc[candidates["expected_revenue"].idxmax()]

    else:
        selected_row = candidates.loc[candidates["expected_revenue"].idxmax()]

    recommended_price = float(selected_row["price"])

    # Final safety check. This should almost never trigger, but it protects trust.
    if recommended_price < minimum_allowed_price:
        selected_row = estimate_price_row(simulation_df, minimum_allowed_price)
        recommended_price = float(selected_row["price"])

    expected_revenue = float(selected_row["expected_revenue"])
    conversion_rate = float(selected_row["conversion_rate"])
    expected_customers = float(selected_row["expected_customers"])
    market_position = classify_market_position(recommended_price, market_summary)

    guardrail_notes = []

    if floor_price is not None:
        guardrail_notes.append(
            f"Applied cost floor guardrail: recommendation must stay at or above ${float(floor_price):.2f}."
        )

    if positioning == "premium" or objective == "premium_positioning":
        guardrail_notes.append(
            "Applied premium positioning guardrail: recommendation should not race to the bottom of the market."
        )

    if floor_price is not None and float(floor_price) > median_price:
        guardrail_notes.append(
            "Strategic warning: the cost floor is above the market median, so growth pricing is constrained. Consider stronger premium positioning, bundling, or reducing costs."
        )

    guardrail_note = " ".join(guardrail_notes) if guardrail_notes else None

    return {
        "recommended_price": round(recommended_price, 2),
        "expected_revenue": round(expected_revenue, 2),
        "conversion_rate": round(conversion_rate, 4),
        "expected_customers": round(expected_customers, 0),
        "market_position": market_position,
        "positioning": positioning,
        "period": "month",
        "objective": objective,
        "guardrail_note": guardrail_note,
        "reason": (
            f"The recommended price is ${recommended_price:.2f}. "
            f"This price is estimated to convert {conversion_rate:.2%} of shoppers, "
            f"producing about {expected_customers:.0f} customers and "
            f"${expected_revenue:.2f} in monthly revenue. "
            f"It positions the product as a {market_position} option."
        ),
    }


def run_pricing_agent(category):
    user_prompt = category.strip()
    steps = []

    parsed = parse_pricing_prompt(user_prompt)
    parsed["raw_context"] = user_prompt
    strategy_profile = build_strategy_profile(parsed)

    product_query = parsed.get("product_query") or ""
    objective = parsed.get("objective", "maximize_revenue")
    audience = parsed.get("audience")
    positioning = parsed.get("positioning")
    cost_floor = extract_cost_floor_from_text(user_prompt)

    if not product_query:
        return {
            "needs_clarification": True,
            "clarifying_question": "What product are you trying to price?",
            "suggested_answers": [
                "Wireless headphones",
                "Standing desk",
                "DJ turntables",
                "Skincare product",
            ],
            "parsed_prompt": parsed,
            "strategy_profile": strategy_profile,
            "product_query": "",
            "user_prompt": user_prompt,
            "steps": ["No product query found."],
        }

    steps.append(f"Built strategy profile for: {product_query}")
    steps.append(f"Detected objective: {objective}")

    if audience:
        steps.append(f"Detected audience: {audience}")

    if positioning:
        steps.append(f"Detected positioning: {positioning}")

    if cost_floor:
        steps.append(f"Detected price floor / cost constraint: ${cost_floor:.2f}")

    try:
        rows = fetch_google_shopping_results(product_query)
    except Exception as e:
        rows = []
        steps.append(f"Live search failed, using fallback demo data instead: {e}")

    if rows:
        category_df = pd.DataFrame(rows)
        steps.append(f"Fetched {len(category_df)} live products from Google Shopping.")
    else:
        category_df = get_real_saas_pricing_data()
        steps.append(
            "Live market data was unavailable, so the agent used curated demo competitor data."
        )

    if category_df.empty:
        return {
            "error": "No usable product data found. Try a broader product category.",
            "steps": steps,
            "parsed_prompt": parsed,
            "strategy_profile": strategy_profile,
            "product_query": product_query,
            "user_prompt": user_prompt,
        }

    steps.append("Calculated market pricing benchmarks.")

    market_summary = summarize_market(category_df)

    steps.append("Simulated revenue across possible price points.")

    simulation_df = simulate_revenue(market_summary)

    steps.append("Selected the price based on objective and guardrails.")

    base_recommendation = recommend_price(
        simulation_df,
        market_summary,
        objective=objective,
        positioning=positioning,
    )

    recommendation = select_guardrailed_price(
        simulation_df=simulation_df,
        market_summary=market_summary,
        objective=objective,
        positioning=positioning,
        floor_price=cost_floor,
    )

    if recommendation["recommended_price"] != base_recommendation["recommended_price"]:
        steps.append(
            f"Adjusted raw recommendation from ${base_recommendation['recommended_price']:.2f} "
            f"to ${recommendation['recommended_price']:.2f} based on strategy guardrails."
        )

    steps.append("Generated strategy explanation.")

    explanation = generate_business_explanation(
        category=product_query,
        market_summary=market_summary,
        recommendation=recommendation,
        objective=objective,
    )

    return {
        "needs_clarification": False,
        "steps": steps,
        "products": category_df,
        "market_summary": market_summary,
        "simulation": simulation_df,
        "recommendation": recommendation,
        "explanation": explanation,
        "parsed_prompt": parsed,
        "strategy_profile": strategy_profile,
        "product_query": product_query,
        "user_prompt": user_prompt,
    }