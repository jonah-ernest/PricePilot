import os
import sys
import html
import json
import markdown
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from src.agent import run_pricing_agent
from src.llm_reasoning import generate_business_explanation, generate_followup_suggestions

app = FastAPI(title="PricePilot")
RESULT_CACHE = {}

STYLE = """
<style>
    :root {
        --bg: #f5f8fb;
        --card: #ffffff;
        --text: #101828;
        --muted: #667085;
        --border: #d9e2ec;
        --accent: #0077b6;
        --accent-dark: #005f92;
        --accent-light: #e0f4ff;
        --green: #137333;
        --green-bg: #eaf8ef;
        --shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    }

    * { box-sizing: border-box; }

    body {
        margin: 0;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--text);
    }

    .topbar {
        background: white;
        border-bottom: 1px solid var(--border);
        padding: 16px 24px;
        display: flex;
        align-items: center;
        gap: 14px;
        position: sticky;
        top: 0;
        z-index: 20;
    }

    .logo {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        background: var(--accent);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 22px;
    }

    .topbar-title {
        font-weight: 800;
        font-size: 18px;
    }

    .topbar-subtitle {
        color: var(--muted);
        font-size: 14px;
    }

    .home-page {
        max-width: 980px;
        margin: 0 auto;
        padding: 36px 22px 120px;
    }

    .chat-panel {
        min-width: 0;
        height: 100%;
        overflow-y: auto;
        padding-bottom: 160px;  /* increase this */
    }

    .dashboard-panel {
        min-width: 0;
        height: 100%;
        overflow-y: auto;
        padding-right: 4px;
    }

    .chat-panel,
    .dashboard-panel {
        display: flex;
        flex-direction: column;
    }

    .message-row {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
        align-items: flex-start;
    }

    .message-row.user {
        justify-content: flex-end;
    }

    .avatar {
        min-width: 38px;
        height: 38px;
        border-radius: 50%;
        background: var(--accent);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
    }

    .avatar.user-avatar {
        background: #e8eef5;
        color: #344054;
    }

    .bubble {
        background: white;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 16px;
        box-shadow: var(--shadow);
        max-width: 760px;
        line-height: 1.45;
        font-size: 14px;
    }

    .user-bubble {
        background: var(--accent);
        color: white;
        border-radius: 18px;
        padding: 12px 16px;
        max-width: 620px;
        font-weight: 650;
        box-shadow: var(--shadow);
        font-size: 14px;
    }

    h1 {
        font-size: 24px;
        margin: 0 0 14px;
        letter-spacing: -0.5px;
    }

    h2 {
        font-size: 18px;
        margin: 0 0 12px;
    }

    h3 {
        font-size: 15px;
        margin: 18px 0 8px;
    }

    p {
        color: var(--muted);
        margin: 8px 0;
        line-height: 1.55;
        font-size: 14px;
    }

    ul {
        margin-top: 8px;
        padding-left: 22px;
    }

    li {
        margin-bottom: 8px;
        font-size: 14px;
    }

    .prompt-card, .card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 24px;
        box-shadow: var(--shadow);
    }

    textarea, input {
        width: 100%;
        border: 1px solid var(--border);
        outline: none;
        font-size: 16px;
        padding: 15px;
        border-radius: 16px;
        font-family: inherit;
        background: white;
    }

    textarea {
        min-height: 120px;
        resize: vertical;
    }

    button, .button {
        border: none;
        background: var(--accent);
        color: white;
        padding: 13px 18px;
        border-radius: 14px;
        font-weight: 800;
        font-size: 14px;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    button:hover, .button:hover {
        background: var(--accent-dark);
    }

    .examples {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 18px;
    }

    .chip {
        border: 1px solid var(--border);
        background: #f8fafc;
        color: #344054;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 13px;
        cursor: pointer;
        font-weight: 600;

        max-width: 100%;
        white-space: normal;   /* 🔥 allows wrapping */
        line-height: 1.3;
    }

    .chip:hover {
        background: var(--accent-light);
        border-color: #bae6fd;
    }

    .grid {
        display: grid;
        gap: 14px;
    }

    .grid-3 {
        grid-template-columns: repeat(3, 1fr);
    }

    .grid-4 {
        grid-template-columns: repeat(4, 1fr);
    }

    .mini-card {
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
    }

    .metric-label {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 22px;
        font-weight: 900;
    }

    .recommendation {
        background: var(--green-bg);
        border-left: 5px solid var(--green);
        border-radius: 16px;
        padding: 18px;
        margin: 16px 0;
    }

    .recommendation h2 {
        color: var(--green);
    }

    .recommendation-price {
        font-size: 40px;
        font-weight: 950;
        color: var(--green);
        margin: 6px 0;
    }

    .section-card {
        margin-top: 18px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
    }

    .app-container {
        display: grid;
        grid-template-columns: 48% 52%;
        gap: 20px;
        height: calc(100vh - 74px);
        padding: 18px;
        overflow: hidden;
    }

    .chat-panel {
        min-width: 0;
        height: 100%;
        overflow-y: auto;
        padding-bottom: 24px;
        display: flex;
        flex-direction: column;
    }

    .dashboard-panel {
        min-width: 0;
        height: 100%;
        overflow-y: auto;
        padding-right: 4px;
    }

    .bottom-input {
        position: sticky;
        bottom: 0;
        background: var(--bg);
        border-top: 1px solid var(--border);
        padding: 12px 0 4px;
        margin-top: auto;
        z-index: 20;
    }

    .bottom-input-inner {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .bottom-input input {
        flex: 1;
        margin: 0;
    }

    .table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 13px;
        margin-top: 10px;
        overflow: hidden;
        border-radius: 14px;
    }

    .table tr:last-child td {
        border-bottom: none;
    }

    .table th {
        background: #f8fafc;
        text-align: left;
        padding: 10px;
        border-bottom: 1px solid var(--border);
        color: #475467;
    }

    .table td {
        padding: 10px;
        border-bottom: 1px solid var(--border);
    }

    .bottom-input-inner {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .bottom-input input {
        flex: 1;
        margin: 0;
    }

    .small-note {
        font-size: 13px;
        color: var(--muted);
    }

    .agent-answer p:first-child {
        background: var(--green-bg);
        border-left: 5px solid var(--green);
        padding: 12px 14px;
        border-radius: 12px;
    }

    .app-container {
        display: grid;
        grid-template-columns: 48% 52%;
        gap: 20px;
        height: calc(100vh - 74px);
        padding: 18px;
        overflow: hidden;
    }

    .chat-panel {
        min-width: 0;
        height: 100%;
        overflow-y: auto;
        padding-bottom: 110px;
    }

    .dashboard-panel {
        min-width: 0;
        height: 100%;
        overflow-y: auto;
        padding-right: 4px;
    }

    .home-page {
        max-width: 1050px;
        margin: 0 auto;
        padding: 56px 22px 120px;
    }

    .prompt-card {
        margin-top: 18px;
    }

    .prompt-card textarea {
        font-size: 18px;
        line-height: 1.5;
    }

    .examples {
        margin-top: 24px;
    }

    .chip {
        background: white;
        border: 1px solid var(--border);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        white-space: normal;
        line-height: 1.3;
    }

    @media (max-width: 900px) {
        .app-container {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 850px) {
        .grid-3, .grid-4 {
            grid-template-columns: 1fr;
        }

        .avatar {
            display: none;
        }

        .bottom-input-inner {
            flex-direction: column;
        }

        button, .button {
            width: 100%;
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


def safe_text(value):
    return html.escape(str(value or ""), quote=True)


def encode_history(history):
    return html.escape(json.dumps(history), quote=True)


def decode_history(history_json):
    try:
        return json.loads(history_json) if history_json else []
    except Exception:
        return []


def render_topbar():
    return """
    <div class="topbar">
        <div class="logo">↗</div>
        <div>
            <div class="topbar-title">Pricing Strategy Agent</div>
            <div class="topbar-subtitle">AI analyst + live pricing dashboard</div>
        </div>
    </div>
    """


def render_history(history):
    html_parts = ""

    for item in history:
        role = item.get("role")
        content = item.get("content", "")

        if role == "user":
            html_parts += f"""
            <div class="message-row user">
                <div class="user-bubble">{safe_text(content)}</div>
                <div class="avatar user-avatar">👤</div>
            </div>
            """
        else:
            html_parts += f"""
            <div class="message-row">
                <div class="avatar">✦</div>
                <div class="bubble agent-answer">
                    {markdown.markdown(content.strip(), extensions=["extra"])}
                </div>
            </div>
            """

    return html_parts


def make_simulation_table(sim):
    display = sim.sort_values("expected_revenue", ascending=False).head(5).rename(
        columns={
            "price": "Price",
            "conversion_rate": "Conversion",
            "expected_customers": "Customers",
            "expected_revenue": "Revenue",
        }
    )

    display["Price"] = display["Price"].apply(price)
    display["Conversion"] = display["Conversion"].apply(percent)
    display["Customers"] = display["Customers"].apply(lambda x: f"{float(x):,.0f}")
    display["Revenue"] = display["Revenue"].apply(money)

    keep_cols = [c for c in ["Price", "Conversion", "Customers", "Revenue"] if c in display.columns]
    return display[keep_cols].to_html(index=False, classes="table", escape=False)


def make_products_table(products_df):
    cols = [
        c for c in ["product_name", "name", "title", "price", "rating", "reviews", "source"]
        if c in products_df.columns
    ]

    if not cols:
        return "<p>No product details available.</p>"

    display = products_df[cols].head(6).copy()

    if "price" in display.columns:
        display["price"] = display["price"].apply(price)

    if "rating" in display.columns:
        display["rating"] = display["rating"].apply(
            lambda x: f"{float(x):.1f}" if str(x) != "nan" else ""
        )

    return display.to_html(index=False, classes="table", escape=False)


def suggested_questions(result, history=None):
    history = history or []
    parsed_prompt = result.get("parsed_prompt", {})
    objective = parsed_prompt.get("objective", "maximize_revenue")

    recent_context = "\n".join(
        f"{item.get('role')}: {item.get('content')[:300]}"
        for item in history[-4:]
    )

    try:
        return generate_followup_suggestions(
            category=result.get("product_query", "product"),
            market_summary=result["market_summary"],
            recommendation=result["recommendation"],
            objective=f"{objective}\nRecent conversation:\n{recent_context}",
        )
    except Exception:
        return [
            "What are the risks of this price?",
            "How would growth pricing change this?",
            "What competitors matter most?",
            "Should I launch with a discount?",
        ]


def make_revenue_chart(sim, recommended_price):
    chart_df = sim.sort_values("price").copy()

    if len(chart_df) > 18:
        chart_df = chart_df.iloc[:: max(1, len(chart_df) // 18)]

    max_revenue = chart_df["expected_revenue"].max()

    bars = ""
    for _, row in chart_df.iterrows():
        height = max(8, (row["expected_revenue"] / max_revenue) * 120)
        is_best = abs(row["price"] - recommended_price) < 0.01
        bar_color = "var(--accent)" if is_best else "#bae6fd"

        bars += f"""
        <div style="flex:1; text-align:center;">
            <div style="
                height:{height}px;
                background:{bar_color};
                border-radius:8px 8px 0 0;
                margin-bottom:6px;
            " title="{price(row['price'])} → {money(row['expected_revenue'])}"></div>
            <div style="font-size:11px; color:var(--muted);">{price(row['price'])}</div>
        </div>
        """

    return f"""
    <div style="
        display:flex;
        align-items:end;
        gap:6px;
        height:160px;
        border-bottom:1px solid var(--border);
        margin-top:12px;
        padding-top:20px;
    ">
        {bars}
    </div>
    <p class="small-note">
        Blue bar = recommended price with strongest expected revenue.
    </p>
    """

def render_dashboard(result):
    summary = result["market_summary"]
    rec = result["recommendation"]
    sim = result["simulation"].copy()
    products_df = result["products"].copy()
    parsed_prompt = result.get("parsed_prompt", {})

    product_query = result.get("product_query", "Product")
    objective = parsed_prompt.get("objective", "maximize_revenue")
    audience = parsed_prompt.get("audience")
    positioning = parsed_prompt.get("positioning")

    sim_html = make_simulation_table(sim)
    chart_html = make_revenue_chart(sim, rec["recommended_price"])
    products_html = make_products_table(products_df)

    return f"""
    <div class="card">
        <h2>Live Pricing Dashboard</h2>
        <p class="small-note">Updates from the latest agent analysis.</p>

        <div class="mini-card">
            <div class="metric-label">Product Search</div>
            <div class="metric-value">{safe_text(product_query.title())}</div>
            <p>
                Objective: <strong>{safe_text(objective.replace("_", " ").title())}</strong><br>
                Audience: <strong>{safe_text(audience or "Not specified")}</strong><br>
                Positioning: <strong>{safe_text(positioning or "Not specified")}</strong>
            </p>
        </div>

        <div class="recommendation">
            <h2>✅ Final Recommendation</h2>
            <div class="recommendation-price">{price(rec["recommended_price"])}</div>
            <p>
                Charge <strong>{price(rec["recommended_price"])}</strong> based on the live competitor benchmark
                and revenue simulation.
            </p>
            <p>
                Expected revenue: <strong>{money(rec["expected_revenue"])}</strong><br>
                Estimated conversion: <strong>{percent(rec["conversion_rate"])}</strong><br>
                Market position: <strong>{safe_text(rec["market_position"])}</strong>
            </p>
        </div>

        <div class="grid grid-3">
            <div class="mini-card">
                <div class="metric-label">Market Median</div>
                <div class="metric-value">{price(summary["median_price"])}</div>
            </div>
            <div class="mini-card">
                <div class="metric-label">Products Analyzed</div>
                <div class="metric-value">{int(summary["num_products"])}</div>
            </div>
            <div class="mini-card">
                <div class="metric-label">Price Range</div>
                <div class="metric-value">{price(summary["min_price"])}–{price(summary["max_price"])}</div>
            </div>
        </div>

        <div class="section-card">
            <h3>Revenue vs Price</h3>
            {chart_html}
            {sim_html}
        </div>

        <div class="section-card">
            <h3>Competitor Snapshot</h3>
            {products_html}
        </div>
    </div>
    """


def render_results_page(category, result, history, session_id):
    history_value = encode_history(history)
    dashboard_html = render_dashboard(result)

    suggestions = suggested_questions(result, history)

    suggestion_buttons = "".join(
        f"""
        <form action="/ask" method="post" style="display:inline;">
            <input type="hidden" name="category" value="{safe_text(category)}">
            <input type="hidden" name="history" value="{history_value}">
            <input type="hidden" name="session_id" value="{session_id}">
            <input type="hidden" name="question" value="{safe_text(q)}">
            <button class="chip" type="submit">{safe_text(q)}</button>
        </form>
        """
        for q in suggestions
    )

    return f"""
    <html>
        <head>
            <title>PricePilot</title>
            {STYLE}
        </head>
        <body>
            {render_topbar()}

            <main class="app-container">
                <section class="chat-panel">
                    {render_history(history)}

                    <div class="message-row">
                        <div class="avatar">✦</div>
                        <div class="bubble">
                            <h2>Suggested next questions</h2>
                            <div class="suggestions">
                                {suggestion_buttons}
                            </div>
                        </div>
                    </div>

                    <div class="bottom-input">
                        <form class="bottom-input-inner" action="/ask" method="post">
                            <input type="hidden" name="category" value="{safe_text(category)}">
                            <input type="hidden" name="history" value="{history_value}">
                            <input type="hidden" name="session_id" value="{session_id}">
                            <input
                                type="text"
                                name="question"
                                placeholder="Ask a follow-up pricing question..."
                                required
                            />
                            <button type="submit">Send</button>
                        </form>
                    </div>
                </section>

                <aside class="dashboard-panel">
                    {dashboard_html}
                </aside>
            </main>
        </body>
    </html>
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
            {render_topbar()}

            <main class="home-page">
                <div class="message-row">
                    <div class="avatar">✦</div>
                    <div class="bubble">
                        <h1>What should you charge?</h1>
                        <p>
                            Describe your product, audience, and pricing goal. PricePilot will search the market,
                            simulate revenue, and recommend a pricing strategy.
                        </p>
                    </div>
                </div>

                <div class="prompt-card">
                    <form action="/analyze" method="post">
                        <textarea
                            name="category"
                            placeholder="Example: What price should I charge for wireless headphones?"
                            required
                        >What price should I charge for wireless headphones?</textarea>

                        <div style="display:flex; justify-content:flex-end; margin-top:12px;">
                            <button type="submit">Analyze Pricing →</button>
                        </div>
                    </form>

                    <div class="examples">
                        <span class="chip" onclick="fillExample('What price should I charge for wireless headphones?')">
                            What price should I charge for wireless headphones?
                        </span>

                        <span class="chip" onclick="fillExample('How should I price sustainable sneakers for eco-conscious millennials?')">
                            How should I price sustainable sneakers for eco-conscious millennials?
                        </span>

                        <span class="chip" onclick="fillExample('I sell a budget standing desk for remote workers. What price helps me grow fast?')">
                            I sell a budget standing desk for remote workers. What price helps me grow fast?
                        </span>

                        <span class="chip" onclick="fillExample('I sell premium skincare and want luxury positioning. What price should I charge?')">
                            I sell premium skincare and want luxury positioning. What price should I charge?
                        </span>

                        <span class="chip" onclick="fillExample('How should I price a productivity SaaS tool with three tiers?')">
                            How should I price a productivity SaaS tool with three tiers?
                        </span>
                    </div>

                    <p class="small-note">
                        You can include product, audience, goal, positioning, price range, COGS, or assumptions.
                    </p>
                </div>
            </main>

            <script>
                function fillExample(value) {{
                    document.querySelector('textarea[name="category"]').value = value;
                }}
            </script>
        </body>
    </html>
    """


@app.post("/analyze", response_class=HTMLResponse)
def analyze(category: str = Form(...)):
    try:
        result = run_pricing_agent(category)
    except Exception as e:
        result = {"error": str(e)}

    if "error" in result:
        return f"""
        <html>
            <head>
                <title>PricePilot</title>
                {STYLE}
            </head>
            <body>
                {render_topbar()}
                <main class="home-page">
                    <div class="message-row user">
                        <div class="user-bubble">{safe_text(category)}</div>
                        <div class="avatar user-avatar">👤</div>
                    </div>

                    <div class="message-row">
                        <div class="avatar">✦</div>
                        <div class="bubble">
                            <h2>I need a little more information.</h2>
                            <p>{safe_text(result["error"])}</p>
                            <a class="button" href="/">Try another prompt</a>
                        </div>
                    </div>
                </main>
            </body>
        </html>
        """

    rec = result["recommendation"]
    product_query = result.get("product_query", category)

    summary_text = (
        f"✅ **Recommendation:** Charge **{price(rec['recommended_price'])}** "
        f"for **{product_query.title()}**.\n\n"
        f"Estimated monthly revenue: **{money(rec['expected_revenue'])}**.  \n"
        f"Estimated conversion: **{percent(rec['conversion_rate'])}**.  \n"
        f"Market position: **{rec['market_position']}**."
    )

    history = [
        {"role": "user", "content": category},
        {"role": "agent", "content": summary_text},
    ]

    session_id = str(uuid.uuid4())
    RESULT_CACHE[session_id] = result

    return render_results_page(category, result, history, session_id)


@app.post("/ask", response_class=HTMLResponse)
def ask(
    question: str = Form(...),
    category: str = Form(...),
    history: str = Form(""),
    session_id: str = Form(""),
):
    chat_history = decode_history(history)
    chat_history.append({"role": "user", "content": question})

    result = RESULT_CACHE.get(session_id)

    if result is None:
        answer = "I lost the previous pricing analysis. Please start a new analysis."
        chat_history.append({"role": "agent", "content": answer})
        return render_results_page(category, run_pricing_agent(category), chat_history, session_id)

    answer = generate_business_explanation(
        category=result.get("product_query", category),
        market_summary=result["market_summary"],
        recommendation=result["recommendation"],
        question=question,
    )

    final_answer = generate_business_explanation(
        category=result.get("product_query", category),
        market_summary=result["market_summary"],
        recommendation=result["recommendation"],
        question=f"Give a one-sentence direct final answer to this question: {question}",
    )

    formatted_answer = f"**Final answer:** {final_answer}\n\n{answer}"

    chat_history.append({"role": "agent", "content": formatted_answer})

    return render_results_page(category, result, chat_history, session_id)