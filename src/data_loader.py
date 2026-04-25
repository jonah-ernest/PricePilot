import pandas as pd


def load_product_data(path="data/products.csv"):
    return pd.read_csv(path)


def filter_by_category(df, category):
    return df[df["category"].str.lower().str.strip() == category.lower().strip()]


def get_available_categories(path="data/products.csv"):
    df = load_product_data(path)
    return sorted(df["category"].dropna().unique().tolist())