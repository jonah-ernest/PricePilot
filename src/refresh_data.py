import os
import requests
import pandas as pd
from datetime import date
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

CATEGORIES = [
    "protein powder",
    "skincare",
    "wireless headphones",
]


def fetch_google_shopping_results(category, limit=30):
    if not SERPAPI_KEY:
        raise ValueError("Missing SERPAPI_KEY in .env")

    params = {
        "engine": "google_shopping",
        "q": category,
        "api_key": SERPAPI_KEY,
    }

    response = requests.get("https://serpapi.com/search.json", params=params)
    response.raise_for_status()

    data = response.json()
    results = data.get("shopping_results", [])

    rows = []

    for item in results[:limit]:
        price_text = item.get("price", "")
        price = (
            price_text.replace("$", "")
            .replace(",", "")
            .split()[0]
            if price_text
            else None
        )

        try:
            price = float(price)
        except:
            continue

        if price < 3 or price > 300:
            continue

        rows.append({
            "product_name": item.get("title"),
            "category": category,
            "price": price,
            "rating": item.get("rating"),
            "num_reviews": item.get("reviews"),
            "source": item.get("source"),
            "source_url": item.get("link"),
            "last_updated": date.today().isoformat(),
        })

    return rows


def refresh_data():
    all_rows = []

    for category in CATEGORIES:
        print(f"Fetching data for: {category}")
        rows = fetch_google_shopping_results(category)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_csv("data/products.csv", index=False)

    print(f"Saved {len(df)} rows to data/products.csv")


if __name__ == "__main__":
    refresh_data()