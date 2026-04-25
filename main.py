import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from src.agent import run_pricing_agent

app = FastAPI()


STYLE = """
<style>
    body {
        font-family: Arial, sans-serif;
        background: #f6f8fb;
        margin: 0;
        padding: 0;
        color: #1f2937;
    }

    .container {
        max-width: 1100px;
        margin: 40px auto;
        padding: 20px;
    }

    .hero {
        background: white;
        padding: 32px;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        margin-bottom: 24px;
    }

    h1 {
        margin-bottom: 8px;
        font-size: 42px;
    }

    h2 {
        margin-top: 0;
    }

    .subtitle {
        color: #6b7280;
        font-size: 18px;
    }

    .form-box {
        margin-top: 24px;
    }

    input {
        padding: 12px;
        width: 360px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        font-size: 16px;
    }

    button {
        padding: 12px 18px;
        border: none;
        background: #2563eb;
        color: white;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;
    }

    button:hover {
        background: #1d4ed8;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 20px;
    }

    .card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    .metric {
        font-size: 32px;
        font-weight: bold;
        color: #2563eb;
    }

    .small {
        color: #6b7280;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        background: white;
    }

    th, td {
        border-bottom: 1px solid #e5e7eb;
        padding: 10px;
        text-align: left;
    }

    th {
        background: #f3f4f6;
    }

    .bar-wrapper {
        margin: 8px 0;
    }

    .bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        margin-bottom: 4px;
    }

    .bar-bg {
        background: #e5e7eb;
        border-radius: 999px;
        overflow: hidden;
        height: 14px;
    }

    .bar {
        background: #2563eb;
        height: 14px;
    }

    .steps li {
        margin-bottom: 8px;
    }

    a {
        color: #2563eb;
        text-decoration: none;
    }

    .result-hero {
        background: linear-gradient(135deg, #ffffff 0%, #eef4ff 100%);
        padding: 36px;
        border-radius: 20px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 24px;
    }

    .category-pill {
        display: inline-block;
        background: #dbeafe;
        color: #1d4ed8;
        padding: 8px 14px;
        border-radius: 999px;
        font-weight: bold;
        margin-bottom: 12px;
    }

    .hero-category {
        font-size: 44px;
        font-weight: 800;
        margin: 8px 0;
        color: #111827;
        text-transform: capitalize;
    }

    .hero-subtext {
        color: #6b7280;
        font-size: 18px;
        max-width: 800px;
    }

    .recommendation-box {
        background: #2563eb;
        color: white;
        padding: 28px;
        border-radius: 20px;
        margin-bottom: 24px;
    }

    .recommendation-box h2 {
        color: white;
    }

    .recommendation-main {
        font-size: 56px;
        font-weight: 800;
        margin: 8px 0;
    }

    .scenario-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
    }

    .scenario-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
    }

    .scenario-card.best {
        border: 3px solid #2563eb;
        background: #eff6ff;
    }

    .scenario-price {
        font-size: 30px;
        font-weight: 800;
        color: #2563eb;
    }

    .badge {
        display: inline-block;
        background: #2563eb;
        color: white;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .insight-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #e5e7eb;
        padding: 10px 0;
    }

    .table {
        border-radius: 12px;
        overflow: hidden;
        font-size: 14px;
    }

    .table th {
        background: #f9fafb;
        font-weight: 600;
    }
</style>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>
        <head>
            <title>PricePilot</title>
            {STYLE}
        </head>
        <body>
            <div class="container">
                <div class="hero">
                    <h1>PricePilot</h1>
                    <p class="subtitle">
                        An AI pricing agent that benchmarks products, simulates revenue,
                        and recommends a data-driven price.
                    </p>

                    <div class="form-box">
                        <form method="post" action="/analyze">
                            <input 
                                name="category" 
                                placeholder="e.g. protein powder, skincare, wireless headphones"
                            />
                            <button type="submit">Run Pricing Agent</button>
                        </form>
                    </div>

                    <div style="margin-top: 24px;">
                        <p class="small"><strong>Try examples:</strong></p>
                        <div style="display:flex; gap:10px; flex-wrap:wrap;">
                            <button type="button" onclick="fillInput('protein powder')">Protein Powder</button>
                            <button type="button" onclick="fillInput('skincare')">Skincare</button>
                            <button type="button" onclick="fillInput('wireless headphones')">Wireless Headphones</button>
                        </div>
                    </div>

                    <script>
                    function fillInput(value) {{
                        document.querySelector('input[name="category"]').value = value;
                    }}
                    </script>

                </div>
            </div>
        </body>
    </html>
    """


@app.post("/analyze", response_class=HTMLResponse)
def analyze(category: str = Form(...)):
    result = run_pricing_agent(category)

    if "error" in result:
        return f"""
        <html>
            <head>{STYLE}</head>
            <body>
                <div class="container">
                    <div class="card">
                        <h1>No data found</h1>
                        <p>{result['error']}</p>
                        <a href="/">Back</a>
                    </div>
                </div>
            </body>
        </html>
        """

    steps_html = "".join(f"<li>{step}</li>" for step in result["steps"])
    summary = result["market_summary"]
    rec = result["recommendation"]
    explanation = result["explanation"]

    sim = result["simulation"].copy()
    top_sim = sim.sort_values("expected_revenue", ascending=False).head(10)
    top_sim_display = top_sim.rename(columns={
        "price": "Price",
        "conversion_rate": "Conversion Rate",
        "expected_customers": "Expected Customers / Month",
        "expected_revenue": "Estimated Revenue / Month",
        "period": "Period"
    })

    top_sim_display["Conversion Rate"] = top_sim_display["Conversion Rate"].apply(lambda x: f"{x:.2%}")
    top_sim_display["Price"] = top_sim_display["Price"].apply(lambda x: f"${x}")
    top_sim_display["Estimated Revenue / Month"] = top_sim_display["Estimated Revenue / Month"].apply(lambda x: f"${x}")

    sim_html = top_sim_display.to_html(index=False, classes="table")

    scenario_prices = [
        max(sim["price"].min(), rec["recommended_price"] * 0.85),
        rec["recommended_price"],
        min(sim["price"].max(), rec["recommended_price"] * 1.15),
    ]

    scenario_cards_html = '<div class="scenario-grid">'

    for price_point in scenario_prices:
        closest_row = sim.iloc[(sim["price"] - price_point).abs().argsort()[:1]].iloc[0]
        is_best = closest_row["price"] == rec["recommended_price"]

        card_class = "scenario-card best" if is_best else "scenario-card"
        badge = '<div class="badge">Recommended</div>' if is_best else ""

        scenario_cards_html += f"""
        <div class="{card_class}">
            {badge}
            <div class="scenario-price">${closest_row['price']}</div>
            <p class="small">Estimated monthly revenue</p>
            <h3>${closest_row['expected_revenue']}</h3>

            <div class="insight-row">
                <span>Conversion</span>
                <strong>{closest_row['conversion_rate']:.2%}</strong>
            </div>

            <div class="insight-row">
                <span>Customers/month</span>
                <strong>{closest_row['expected_customers']}</strong>
            </div>
        </div>
        """

    scenario_cards_html += "</div>"

    return f"""
    <html>
        <head>
            <title>PricePilot Results</title>
            {STYLE}
        </head>
        <body>
            <div class="container">
                <div class="result-hero">
                    <div class="category-pill">Live Market Analysis</div>
                    <div class="hero-category">"{category}"</div>
                    <p class="hero-subtext">
                        PricePilot pulled real ecommerce product data for this category, benchmarked the market,
                        simulated monthly revenue, and generated a pricing recommendation.
                    </p>
                    <br>
                    <a href="/">Run another analysis</a>
                </div>

                <div class="card">
                    <h2>Estimated Monthly Revenue</h2>
                    <div class="metric">${rec['expected_revenue']}</div>
                    <p class="small">
                        Assumes 1,000 monthly shoppers · Conversion rate: {rec['conversion_rate']:.2%}
                    </p>
                </div>
                </div>

                <div class="card">
                    <h2>Business Explanation</h2>
                    <p>{explanation}</p>
                </div>

                <div class="recommendation-box">
                    <h2>Recommended Pricing Strategy</h2>
                    <p class="small">Optimal price based on real market data</p>
                    <div class="recommendation-main">${rec['recommended_price']}</div>
                    <p>
                        Estimated monthly revenue: <strong>${rec['expected_revenue']}</strong> ·
                        Estimated customers/month: <strong>{rec['expected_customers']}</strong> ·
                        Conversion rate: <strong>{rec['conversion_rate']:.2%}</strong>
                    </p>
                    <p>
                        This positions the product as a <strong>{rec['market_position']}</strong> option in the current market.
                    </p>
                </div>

                <div class="card">
                    <h2>Pricing Scenarios</h2>
                    <p class="small">
                        Estimated monthly outcomes assuming 1,000 monthly shoppers.
                        The highlighted option is the revenue-maximizing price from the simulation.
                    </p>
                    {scenario_cards_html}
                </div>

                <div class="card">
                    <h2>Top Monthly Revenue Scenarios</h2>
                    {sim_html}
                </div>
            </div>
        </body>
    </html>
    """