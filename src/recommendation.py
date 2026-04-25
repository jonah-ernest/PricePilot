def classify_market_position(price, market_summary):
    median_price = market_summary["median_price"]

    if price < median_price * 0.85:
        return "budget"
    elif price <= median_price * 1.15:
        return "mid-market"
    else:
        return "premium"


def recommend_price(simulation_df, market_summary):
    best_row = simulation_df.loc[simulation_df["expected_revenue"].idxmax()]

    recommended_price = float(best_row["price"])
    expected_revenue = float(best_row["expected_revenue"])
    conversion_rate = float(best_row["conversion_rate"])
    expected_customers = float(best_row["expected_customers"])

    market_position = classify_market_position(recommended_price, market_summary)

    return {
        "recommended_price": round(recommended_price, 2),
        "expected_revenue": round(expected_revenue, 2),
        "conversion_rate": round(conversion_rate, 4),
        "expected_customers": round(expected_customers, 0),
        "market_position": market_position,
        "period": "month",
        "reason": (
            f"The recommended price is ${recommended_price:.2f}. "
            f"At an assumed 1,000 monthly shoppers, this price is estimated to convert "
            f"{conversion_rate:.2%} of shoppers, producing about {expected_customers:.0f} "
            f"customers and ${expected_revenue:.2f} in monthly revenue. "
            f"This positions the product as a {market_position} option relative to the market."
        )
    }