def recommend_price(simulation_df, market_summary, objective="maximize_revenue", positioning=None):
    df = simulation_df.copy()

    if objective == "premium_positioning" or positioning == "premium":
        target_price = market_summary["median_price"] * 1.25
        best_row = df.iloc[(df["price"] - target_price).abs().argsort()[:1]].iloc[0]
        market_position = "premium"

    elif objective == "competitive_entry" or positioning == "budget":
        target_price = market_summary["median_price"] * 0.90
        best_row = df.iloc[(df["price"] - target_price).abs().argsort()[:1]].iloc[0]
        market_position = "competitive"

    elif objective == "maximize_growth":
        best_row = df.sort_values("conversion_rate", ascending=False).iloc[0]
        market_position = "growth-focused"

    else:
        best_row = df.sort_values("expected_revenue", ascending=False).iloc[0]

        if best_row["price"] < market_summary["median_price"] * 0.9:
            market_position = "budget"
        elif best_row["price"] > market_summary["median_price"] * 1.15:
            market_position = "premium"
        else:
            market_position = "mid-market"

    return {
        "recommended_price": best_row["price"],
        "expected_revenue": best_row["expected_revenue"],
        "conversion_rate": best_row["conversion_rate"],
        "expected_customers": best_row["expected_customers"],
        "market_position": market_position,
    }