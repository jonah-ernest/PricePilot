from src.scraper import get_real_saas_pricing_data


def build_dataset():
    df = get_real_saas_pricing_data()
    df.to_csv("data/competitors.csv", index=False)
    print("Dataset built from real public SaaS pricing data")
    print(df)


if __name__ == "__main__":
    build_dataset()