def summarize_market(df):
    prices = df["price"]

    return {
        "mean_price": round(prices.mean(), 2),
        "median_price": round(prices.median(), 2),
        "min_price": round(prices.min(), 2),
        "max_price": round(prices.max(), 2),
        "num_products": len(df),
        "avg_rating": round(df["rating"].mean(), 2) if "rating" in df else None,
        "total_reviews": int(df["num_reviews"].sum()) if "num_reviews" in df else None,
    }