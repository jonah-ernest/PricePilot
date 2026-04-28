import pandas as pd

from src.data_loader import load_product_data, filter_by_category
from src.benchmarking import summarize_market
from src.simulation import simulate_revenue
from src.recommendation import recommend_price
from src.llm_reasoning import generate_business_explanation
from src.refresh_data import fetch_google_shopping_results


def log_step(steps, action, tool, result):
    steps.append({"action": action, "tool": tool, "result": result})


def fetch_and_store_category(category):
    rows = fetch_google_shopping_results(category)

    if not rows:
        return None

    new_df = pd.DataFrame(rows)

    try:
        existing_df = pd.read_csv("data/products.csv")
        combined = pd.concat([existing_df, new_df], ignore_index=True)
    except Exception:
        combined = new_df

    combined.to_csv("data/products.csv", index=False)
    return new_df


def run_pricing_agent(
    category,
    base_traffic=1000,
    base_conversion=0.08,
    price_elasticity=1.25,
    objective="maximize_revenue",
):
    category = category.lower().strip()
    steps = []

    log_step(
        steps,
        "Interpret user request",
        "Input parser",
        f"User wants a pricing strategy for: {category}",
    )

    df = load_product_data()

    log_step(
        steps,
        "Load pricing data",
        "Local CSV data loader",
        "Loaded stored product pricing dataset.",
    )

    category_df = filter_by_category(df, category)

    if category_df.empty:
        log_step(
            steps,
            "Decide whether external data is needed",
            "Agent decision logic",
            "No local products found, so live market data will be fetched.",
        )

        category_df = fetch_and_store_category(category)

        if category_df is None or category_df.empty:
            return {
                "error": "No product data found even after API fetch.",
                "steps": steps,
            }

        log_step(
            steps,
            "Fetch live competitor data",
            "Google Shopping / SerpAPI tool",
            f"Fetched {len(category_df)} competitor products and updated the dataset.",
        )
    else:
        log_step(
            steps,
            "Use existing benchmark data",
            "Category filter",
            f"Found {len(category_df)} matching products in the local dataset.",
        )

    market_summary = summarize_market(category_df)

    log_step(
        steps,
        "Benchmark the market",
        "Pricing benchmark tool",
        "Calculated market pricing statistics.",
    )

    simulation_df = simulate_revenue(
        market_summary,
        base_traffic=base_traffic,
        base_conversion=base_conversion,
        price_elasticity=price_elasticity,
    )

    log_step(
        steps,
        "Simulate revenue scenarios",
        "Revenue simulation tool",
        f"Used {base_traffic:,} monthly shoppers, {base_conversion:.1%} base conversion, and {price_elasticity} price elasticity.",
    )

    recommendation = recommend_price(simulation_df, market_summary, objective)

    log_step(
        steps,
        "Choose recommended price",
        "Pricing recommendation tool",
        "Selected the price point with the highest expected monthly revenue.",
    )

    explanation = generate_business_explanation(
        category=category,
        market_summary=market_summary,
        recommendation=recommendation,
        objective=objective,
    )

    log_step(
        steps,
        "Align recommendation with business objective",
        "Strategy objective selector",
        f"Optimizing pricing strategy for objective: {objective}.",
    )

    return {
        "steps": steps,
        "products": category_df,
        "market_summary": market_summary,
        "simulation": simulation_df,
        "recommendation": recommendation,
        "explanation": explanation,
        "inputs": {
            "base_traffic": base_traffic,
            "base_conversion": base_conversion,
            "price_elasticity": price_elasticity,
        },
    }