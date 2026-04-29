def classify_market_position(price, market_summary):
    median_price = market_summary["median_price"]

    if price < median_price * 0.85:
        return "budget"
    elif price <= median_price * 1.15:
        return "mid-market"
    else:
        return "premium"


def recommend_price(
    simulation_df,
    market_summary,
    objective="maximize_revenue",
    positioning=None,
):
    if objective == "maximize_growth":
        selected_row = simulation_df.loc[simulation_df["expected_customers"].idxmax()]

    elif objective == "competitive_entry":
        target_price = market_summary["median_price"] * 0.9
        selected_row = simulation_df.iloc[
            (simulation_df["price"] - target_price).abs().argsort()[:1]
        ].iloc[0]

    elif objective == "premium_positioning":
        premium_df = simulation_df[
            simulation_df["price"] >= market_summary["median_price"] * 1.15
        ]
        selected_row = premium_df.loc[premium_df["expected_revenue"].idxmax()] \
            if not premium_df.empty else simulation_df.loc[simulation_df["expected_revenue"].idxmax()]

    else:
        selected_row = simulation_df.loc[simulation_df["expected_revenue"].idxmax()]

    recommended_price = float(selected_row["price"])
    expected_revenue = float(selected_row["expected_revenue"])
    conversion_rate = float(selected_row["conversion_rate"])
    expected_customers = float(selected_row["expected_customers"])
    market_position = classify_market_position(recommended_price, market_summary)

    return {
        "recommended_price": round(recommended_price, 2),
        "expected_revenue": round(expected_revenue, 2),
        "conversion_rate": round(conversion_rate, 4),
        "expected_customers": round(expected_customers, 0),
        "market_position": market_position,
        "positioning": positioning,
        "period": "month",
        "objective": objective,
        "reason": (
            f"The recommended price is ${recommended_price:.2f}. "
            f"This price is estimated to convert {conversion_rate:.2%} of shoppers, "
            f"producing about {expected_customers:.0f} customers and "
            f"${expected_revenue:.2f} in monthly revenue. "
            f"It positions the product as a {market_position} option."
        ),
    }