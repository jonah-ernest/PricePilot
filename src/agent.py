from src.benchmarking import summarize_market
from src.simulation import simulate_revenue
from src.recommendation import recommend_price
from src.llm_reasoning import generate_business_explanation
from src.refresh_data import fetch_google_shopping_results
from src.prompt_parser import parse_pricing_prompt
import pandas as pd

def run_pricing_agent(category):
    user_prompt = category.strip()
    steps = []

    parsed = parse_pricing_prompt(user_prompt)

    product_query = parsed.get("product_query") or user_prompt
    objective = parsed.get("objective", "maximize_revenue")
    audience = parsed.get("audience")
    positioning = parsed.get("positioning")

    if parsed.get("needs_clarification") and not parsed.get("product_query"):
        return {
            "error": parsed.get("clarifying_question") or "Please describe the product you want to price.",
            "steps": ["Parsed prompt and determined more information is needed."],
        }

    steps.append(f"Parsed user request into product search: {product_query}")
    steps.append(f"Detected objective: {objective}")
    if audience:
        steps.append(f"Detected audience: {audience}")
    if positioning:
        steps.append(f"Detected positioning: {positioning}")

    rows = fetch_google_shopping_results(product_query)

    if not rows:
        return {
            "error": "No live product data found. Try a broader search like 'wireless headphones' or 'protein powder'.",
            "steps": steps,
        }

    category_df = pd.DataFrame(rows)

    if category_df.empty:
        return {
            "error": "No usable products found from the live search.",
            "steps": steps,
        }

    steps.append(f"Fetched {len(category_df)} live products from Google Shopping.")
    steps.append("Calculated market pricing benchmarks.")

    market_summary = summarize_market(category_df)

    steps.append("Simulated revenue across possible price points.")

    simulation_df = simulate_revenue(market_summary)

    steps.append("Selected the price with the highest expected revenue.")

    recommendation = recommend_price(
        simulation_df,
        market_summary,
        objective=objective,
        positioning=positioning,
    )

    steps.append("Generated business explanation.")

    explanation = generate_business_explanation(
        category=product_query,
        market_summary=market_summary,
        recommendation=recommendation,
    )

    return {
        "steps": steps,
        "products": category_df,
        "market_summary": market_summary,
        "simulation": simulation_df,
        "recommendation": recommendation,
        "explanation": explanation,
        "parsed_prompt": parsed,
        "product_query": product_query,
        "user_prompt": user_prompt,
    }