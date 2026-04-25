import pandas as pd


def get_real_saas_pricing_data():
    """
    Real competitor pricing data curated from public SaaS pricing pages.
    This avoids unreliable live scraping during the demo.
    """

    data = [
        {
            "product_name": "Asana",
            "category": "project management SaaS",
            "price": 10.99,
            "tier": "budget",
            "features": "tasks; projects; collaboration"
        },
        {
            "product_name": "Trello",
            "category": "project management SaaS",
            "price": 5.00,
            "tier": "budget",
            "features": "boards; cards; basic automation"
        },
        {
            "product_name": "ClickUp",
            "category": "project management SaaS",
            "price": 7.00,
            "tier": "budget",
            "features": "tasks; docs; dashboards"
        },
        {
            "product_name": "Notion",
            "category": "project management SaaS",
            "price": 10.00,
            "tier": "budget",
            "features": "docs; wikis; projects"
        },
        {
            "product_name": "Monday.com",
            "category": "project management SaaS",
            "price": 12.00,
            "tier": "mid",
            "features": "workflows; dashboards; automations"
        },
        {
            "product_name": "Smartsheet",
            "category": "project management SaaS",
            "price": 9.00,
            "tier": "budget",
            "features": "sheets; project tracking; reports"
        },
        {
            "product_name": "Wrike",
            "category": "project management SaaS",
            "price": 9.80,
            "tier": "budget",
            "features": "project planning; dashboards; collaboration"
        },
        {
            "product_name": "Basecamp",
            "category": "project management SaaS",
            "price": 15.00,
            "tier": "mid",
            "features": "projects; messaging; file sharing"
        },
        {
            "product_name": "Airtable",
            "category": "project management SaaS",
            "price": 20.00,
            "tier": "mid",
            "features": "databases; workflows; interfaces"
        },
        {
            "product_name": "Teamwork",
            "category": "project management SaaS",
            "price": 10.99,
            "tier": "budget",
            "features": "client work; time tracking; projects"
        },
    ]

    return pd.DataFrame(data)