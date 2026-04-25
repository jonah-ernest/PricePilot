import pandas as pd


def simulate_revenue(market_summary, base_traffic=1000, period="month"):
    median_price = market_summary["median_price"]
    min_market_price = market_summary["min_price"]
    max_market_price = market_summary["max_price"]

    # Keep simulation close to observed market range
    min_price = max(1, int(min_market_price * 0.8))
    max_price = int(max_market_price * 1.1)

    rows = []

    for price in range(min_price, max_price + 1):
        price_ratio = price / median_price

        # More realistic conversion curve
        conversion_rate = 0.08 * (1 / price_ratio) ** 1.25

        # Penalize prices below market floor
        if price < min_market_price:
            conversion_rate *= price / min_market_price

        # Penalize prices far above median more aggressively
        if price > median_price:
            conversion_rate *= (median_price / price) ** 0.8

        conversion_rate = min(max(conversion_rate, 0.005), 0.20)

        expected_customers = base_traffic * conversion_rate
        expected_revenue = expected_customers * price

        rows.append({
            "price": round(price, 2),
            "conversion_rate": round(conversion_rate, 4),
            "expected_customers": round(expected_customers, 0),
            "expected_revenue": round(expected_revenue, 2),
            "period": period
        })

    return pd.DataFrame(rows)