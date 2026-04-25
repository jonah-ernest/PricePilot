from src.data_loader import load_product_data, filter_by_category
from src.benchmarking import summarize_market
from src.simulation import simulate_revenue
from src.recommendation import recommend_price
from src.llm_reasoning import generate_business_explanation
from src.refresh_data import fetch_google_shopping_results
import pandas as pd


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


def run_pricing_agent(category):
    category = category.lower().strip()
    steps = []

    steps.append("Loaded real product pricing dataset.")
    df = load_product_data()

    steps.append(f"Filtered products for category: {category}.")
    category_df = filter_by_category(df, category)

    if category_df.empty:
        steps.append("No local data found. Fetching real product data from API...")
        category_df = fetch_and_store_category(category)

        if category_df is None or category_df.empty:
            return {
                "error": "No product data found even after API fetch.",
                "steps": steps
            }

        steps.append("Fetched real data and updated dataset.")

    steps.append("Calculated market pricing benchmarks.")
    market_summary = summarize_market(category_df)

    steps.append("Simulated revenue across possible price points.")
    simulation_df = simulate_revenue(market_summary)

    steps.append("Selected the price with the highest expected revenue.")
    recommendation = recommend_price(simulation_df, market_summary)

    steps.append("Generated business explanation.")
    explanation = generate_business_explanation(
        category=category,
        market_summary=market_summary,
        recommendation=recommendation
    )

    return {
        "steps": steps,
        "products": category_df,
        "market_summary": market_summary,
        "simulation": simulation_df,
        "recommendation": recommendation,
        "explanation": explanation
    }