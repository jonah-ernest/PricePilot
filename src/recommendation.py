def recommend_price(simulation_df, market_summary, objective="maximize_revenue"):
    median_price = market_summary["median_price"]

    if objective == "maximize_growth":
        filtered = simulation_df.sort_values(
            ["expected_customers", "expected_revenue"],
            ascending=False,
        )
        best_row = filtered.iloc[0]
        strategy = "growth"

    elif objective == "competitive_entry":
        target_price = median_price * 0.9
        best_row = simulation_df.iloc[
            (simulation_df["price"] - target_price).abs().argsort()[:1]
        ].iloc[0]
        strategy = "competitive entry"

    elif objective == "premium_positioning":
        premium_options = simulation_df[simulation_df["price"] >= median_price * 1.15]

        if premium_options.empty:
            premium_options = simulation_df[simulation_df["price"] >= median_price]

        if premium_options.empty:
            best_row = simulation_df.sort_values("expected_revenue", ascending=False).iloc[0]
        else:
            best_row = premium_options.sort_values("expected_revenue", ascending=False).iloc[0]

        strategy = "premium positioning"

    else:
        best_row = simulation_df.sort_values("expected_revenue", ascending=False).iloc[0]
        strategy = "revenue maximization"

    recommended_price = float(best_row["price"])

    if recommended_price < median_price * 0.9:
        market_position = "budget"
    elif recommended_price > median_price * 1.1:
        market_position = "premium"
    else:
        market_position = "mid-market"

    return {
        "recommended_price": recommended_price,
        "expected_revenue": float(best_row["expected_revenue"]),
        "conversion_rate": float(best_row["conversion_rate"]),
        "expected_customers": float(best_row["expected_customers"]),
        "market_position": market_position,
        "strategy": strategy,
        "objective": objective,
    }