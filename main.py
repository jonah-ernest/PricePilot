import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from src.agent import run_pricing_agent

app = FastAPI(title="PricePilot")


STYLE = """
<style>
    :root {
        --bg: #f6f8fb;
        --card: #ffffff;
        --text: #172033;
        --muted: #667085;
        --border: #e5e7eb;
        --accent: #2563eb;
        --accent-dark: #1d4ed8;
        --green: #15803d;
        --green-bg: #ecfdf3;
        --blue-bg: #eff6ff;
        --shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
    }

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--text);
    }

    .page {
        max-width: 1180px;
        margin: 0 auto;
        padding: 48px 24px;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        border-radius: 28px;
        padding: 48px;
        box-shadow: var(--shadow);
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 14px;
        margin-bottom: 20px;
    }

    h1 {
        font-size: 52px;
        line-height: 1.05;
        margin: 0 0 16px;
        letter-spacing: -1.4px;
    }

    h2 {
        margin: 0 0 16px;
        font-size: 24px;
    }

    h3 {
        margin: 0 0 8px;
        font-size: 16px;
    }

    p {
        color: var(--muted);
        line-height: 1.6;
    }

    .hero p {
        color: #dbeafe;
        max-width: 720px;
        font-size: 18px;
        margin-bottom: 28px;
    }

    .search-card {
        background: white;
        border-radius: 22px;
        padding: 10px;
        display: flex;
        gap: 10px;
        max-width: 720px;
    }

    input {
        flex: 1;
        border: none;
        outline: none;
        font-size: 17px;
        padding: 16px 18px;
        border-radius: 16px;
    }

    button, .button {
        border: none;
        background: var(--accent);
        color: white;
        padding: 15px 22px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 15px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }

    button:hover, .button:hover {
        background: var(--accent-dark);
    }

    .examples {
        margin-top: 22px;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }

    .example-pill {
        color: white;
        text-decoration: none;
        padding: 9px 14px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.13);
        border: 1px solid rgba(255, 255, 255, 0.18);
        font-size: 14px;
    }

    .section {
        margin-top: 28px;
    }

    .grid {
        display: grid;
        gap: 18px;
    }

    .grid-4 {
        grid-template-columns: repeat(4, 1fr);
    }

    .grid-3 {
        grid-template-columns: repeat(3, 1fr);
    }

    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 24px;
        box-shadow: var(--shadow);
    }

    .metric-label {
        color: var(--muted);
        font-size: 14px;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.8px;
    }

    .metric-subtitle {
        margin-top: 8px;
        color: var(--muted);
        font-size: 14px;
    }

    .hero-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 20px;
        margin-bottom: 24px;
    }

    .query-label {
        color: var(--muted);
        margin-bottom: 6px;
    }

    .query-title {
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .recommendation-card {
        background: linear-gradient(135deg, #eff6ff, #ffffff);
        border: 1px solid #bfdbfe;
    }

    .recommended-price {
        font-size: 56px;
        font-weight: 900;
        letter-spacing: -2px;
        color: #1d4ed8;
        margin: 8px 0;
    }

    .status-pill {
        display: inline-block;
        background: var(--green-bg);
        color: var(--green);
        border: 1px solid #bbf7d0;
        padding: 7px 11px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        text-transform: capitalize;
    }

    .scenario-card {
        position: relative;
        border: 1px solid var(--border);
    }

    .scenario-card.best {
        border: 2px solid var(--accent);
        background: var(--blue-bg);
    }

    .scenario-badge {
        position: absolute;
        right: 18px;
        top: 18px;
        background: var(--accent);
        color: white;
        font-size: 12px;
        padding: 6px 10px;
        border-radius: 999px;
        font-weight: 700;
    }

    .table {
        width: 100%;
        border-collapse: collapse;
        overflow: hidden;
        border-radius: 18px;
        font-size: 14px;
    }

    .table th {
        background: #f8fafc;
        color: #475467;
        text-align: left;
        padding: 14px;
        border-bottom: 1px solid var(--border);
    }

    .table td {
        padding: 14px;
        border-bottom: 1px solid var(--border);
    }

    .steps {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .steps li {
        padding: 13px 0;
        border-bottom: 1px solid var(--border);
        color: #344054;
    }

    .steps li:last-child {
        border-bottom: none;
    }

    .chart {
        display: flex;
        align-items: end;
        gap: 8px;
        height: 260px;
        padding-top: 16px;
        border-bottom: 1px solid var(--border);
    }

    .bar-wrap {
        flex: 1;
        display: flex;
        align-items: end;
        height: 100%;
    }

    .bar {
        width: 100%;
        min-height: 6px;
        border-radius: 8px 8px 0 0;
        background: #93c5fd;
    }

    .bar.best {
        background: #2563eb;
    }

    .chart-labels {
        display: flex;
        justify-content: space-between;
        color: var(--muted);
        font-size: 13px;
        margin-top: 10px;
    }

    .error {
        max-width: 680px;
        margin: 80px auto;
        text-align: center;
    }

    @media (max-width: 900px) {
        .grid-4, .grid-3 {
            grid-template-columns: 1fr;
        }

        .hero {
            padding: 32px;
        }

        h1 {
            font-size: 40px;
        }

        .search-card {
            flex-direction: column;
        }

        .hero-row {
            flex-direction: column;
        }
    }
</style>
"""


def money(value):
    return f"${float(value):,.0f}"


def price(value):
    return f"${float(value):,.2f}"


def percent(value):
    return f"{float(value):.2%}"


def build_chart(sim, recommended_price):
    chart_df = sim.sort_values("price").copy()

    if len(chart_df) > 18:
        chart_df = chart_df.iloc[:: max(1, len(chart_df) // 18)]

    max_revenue = chart_df["expected_revenue"].max()

    bars = ""
    for _, row in chart_df.iterrows():
        height = max(6, (row["expected_revenue"] / max_revenue) * 100)
        is_best = abs(row["price"] - recommended_price) < 0.01
        bar_class = "bar best" if is_best else "bar"

        bars += f"""
            <div class="bar-wrap" title="${row['price']} → ${row['expected_revenue']}">
                <div class="{bar_class}" style="height:{height}%"></div>
            </div>
        """

    return f"""
        <div class="chart">{bars}</div>
        <div class="chart-labels">
            <span>{price(chart_df['price'].min())}</span>
            <span>Revenue simulation across price points</span>
            <span>{price(chart_df['price'].max())}</span>
        </div>
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
            <main class="page">
                <section class="hero">
                    <div class="badge">AI Pricing Strategy Agent</div>
                    <h1>Find the price that maximizes revenue.</h1>
                    <p>
                        PricePilot benchmarks live product data, simulates demand across price points,
                        and recommends a pricing strategy with expected revenue impact.
                    </p>

                    <form class="search-card" action="/analyze" method="post">
                        <input
                            name="category"
                            placeholder="Try wireless headphones, skincare, protein powder..."
                            value="wireless headphones"
                            required
                        />
                        <button type="submit">Analyze Pricing</button>
                    </form>

                    <div class="examples">
                        <a class="example-pill" href="#" onclick="fillExample('wireless headphones')">Wireless Headphones</a>
                        <a class="example-pill" href="#" onclick="fillExample('protein powder')">Protein Powder</a>
                        <a class="example-pill" href="#" onclick="fillExample('skincare')">Skincare</a>
                    </div>
                </section>

                <section class="section grid grid-3">
                    <div class="card">
                        <h3>1. Market Benchmarking</h3>
                        <p>Pulls product prices and summarizes the current competitive landscape.</p>
                    </div>
                    <div class="card">
                        <h3>2. Revenue Simulation</h3>
                        <p>Tests possible prices using conversion and demand assumptions.</p>
                    </div>
                    <div class="card">
                        <h3>3. Strategy Recommendation</h3>
                        <p>Selects the strongest price and explains the business tradeoff.</p>
                    </div>
                </section>
            </main>

            <script>
                function fillExample(value) {{
                    document.querySelector('input[name="category"]').value = value;
                }}
            </script>
        </body>
    </html>
    """


@app.post("/analyze", response_class=HTMLResponse)
def analyze(category: str = Form(...)):
    result = run_pricing_agent(category)

    if "error" in result:
        return f"""
        <html>
            <head>
                <title>No Data Found</title>
                {STYLE}
            </head>
            <body>
                <main class="page">
                    <div class="card error">
                        <h1>No data found</h1>
                        <p>{result["error"]}</p>
                        <a class="button" href="/">Run another analysis</a>
                    </div>
                </main>
            </body>
        </html>
        """

    steps = result["steps"]
    summary = result["market_summary"]
    rec = result["recommendation"]
    explanation = result["explanation"]
    sim = result["simulation"].copy()

    best_price = rec["recommended_price"]
    chart_html = build_chart(sim, best_price)

    top_sim = sim.sort_values("expected_revenue", ascending=False).head(8)
    top_sim_display = top_sim.rename(
        columns={
            "price": "Price",
            "conversion_rate": "Conversion Rate",
            "expected_customers": "Customers / Month",
            "expected_revenue": "Revenue / Month",
            "period": "Period",
        }
    )

    top_sim_display["Price"] = top_sim_display["Price"].apply(price)
    top_sim_display["Conversion Rate"] = top_sim_display["Conversion Rate"].apply(percent)
    top_sim_display["Customers / Month"] = top_sim_display["Customers / Month"].apply(lambda x: f"{float(x):,.0f}")
    top_sim_display["Revenue / Month"] = top_sim_display["Revenue / Month"].apply(money)

    sim_html = top_sim_display.to_html(index=False, classes="table", escape=False)

    scenario_prices = [
        max(sim["price"].min(), best_price * 0.85),
        best_price,
        min(sim["price"].max(), best_price * 1.15),
    ]

    scenario_cards_html = ""

    for label, price_point in zip(["Lower Price", "Recommended", "Higher Price"], scenario_prices):
        closest_row = sim.iloc[(sim["price"] - price_point).abs().argsort()[:1]].iloc[0]
        is_best = label == "Recommended"
        card_class = "card scenario-card best" if is_best else "card scenario-card"
        badge = '<div class="scenario-badge">Best Option</div>' if is_best else ""

        scenario_cards_html += f"""
            <div class="{card_class}">
                {badge}
                <div class="metric-label">{label}</div>
                <div class="metric-value">{price(closest_row["price"])}</div>
                <div class="metric-subtitle">
                    {money(closest_row["expected_revenue"])} monthly revenue
                </div>
                <p>
                    Conversion: {percent(closest_row["conversion_rate"])}<br>
                    Customers/month: {float(closest_row["expected_customers"]):,.0f}
                </p>
            </div>
        """

    steps_html = "".join(f"<li>{step}</li>" for step in steps)

    return f"""
    <html>
        <head>
            <title>PricePilot Results</title>
            {STYLE}
        </head>
        <body>
            <main class="page">
                <div class="hero-row">
                    <div>
                        <div class="query-label">Pricing analysis for</div>
                        <div class="query-title">{category.title()}</div>
                    </div>
                    <a class="button" href="/">Run another analysis</a>
                </div>

                <section class="grid grid-4">
                    <div class="card recommendation-card">
                        <div class="metric-label">Recommended Price</div>
                        <div class="recommended-price">{price(rec["recommended_price"])}</div>
                        <span class="status-pill">{rec["market_position"]}</span>
                    </div>

                    <div class="card">
                        <div class="metric-label">Expected Monthly Revenue</div>
                        <div class="metric-value">{money(rec["expected_revenue"])}</div>
                        <div class="metric-subtitle">Assumes 1,000 monthly shoppers</div>
                    </div>

                    <div class="card">
                        <div class="metric-label">Estimated Conversion</div>
                        <div class="metric-value">{percent(rec["conversion_rate"])}</div>
                        <div class="metric-subtitle">{float(rec["expected_customers"]):,.0f} customers/month</div>
                    </div>

                    <div class="card">
                        <div class="metric-label">Market Median Price</div>
                        <div class="metric-value">{price(summary["median_price"])}</div>
                        <div class="metric-subtitle">
                            Range: {price(summary["min_price"])} - {price(summary["max_price"])}
                        </div>
                    </div>
                </section>

                <section class="section card">
                    <h2>Revenue Simulation</h2>
                    <p>
                        PricePilot simulated monthly revenue across possible prices and selected the
                        price point with the strongest expected revenue.
                    </p>
                    {chart_html}
                </section>

                <section class="section">
                    <h2>Pricing Scenarios</h2>
                    <div class="grid grid-3">
                        {scenario_cards_html}
                    </div>
                </section>

                <section class="section grid grid-3">
                    <div class="card">
                        <div class="metric-label">Products Analyzed</div>
                        <div class="metric-value">{int(summary["num_products"])}</div>
                    </div>
                    <div class="card">
                        <div class="metric-label">Average Price</div>
                        <div class="metric-value">{price(summary["mean_price"])}</div>
                    </div>
                    <div class="card">
                        <div class="metric-label">Price Spread</div>
                        <div class="metric-value">{price(summary["max_price"] - summary["min_price"])}</div>
                    </div>
                </section>

                <section class="section card">
                    <h2>Business Explanation</h2>
                    <p>{explanation}</p>
                </section>

                <section class="section card">
                    <h2>Top Revenue Scenarios</h2>
                    {sim_html}
                </section>

                <section class="section card">
                    <h2>Agent Workflow</h2>
                    <ul class="steps">
                        {steps_html}
                    </ul>
                </section>
            </main>
        </body>
    </html>
    """