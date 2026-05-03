# PricePilot

PricePilot is an AI pricing strategy agent that helps founders and small ecommerce teams choose a launch price using competitor market data, revenue simulation, and LLM-based pricing reasoning.

Instead of forcing users to manually search competitor prices and guess a price point, PricePilot combines market benchmarking, pricing simulation, and advisor-style follow-up questions into one workflow.

## Live Demo

Live URL: **PASTE DEPLOYED URL HERE**

## Product Overview

PricePilot is designed for early-stage founders, ecommerce sellers, and small product teams who are preparing to launch or reposition a product.

The agent helps answer questions like:

- What price should I launch at?
- Am I underpriced or overpriced compared to competitors?
- What happens to revenue if I raise or lower price?
- Should I optimize for growth, revenue, or premium positioning?
- What pricing experiment should I run next?

## Key Features

- Chatbot-style strategy intake
- Structured parsing of the user’s product, target audience, positioning, and pricing goal
- Live competitor price lookup using Google Shopping / SerpApi when available
- Market benchmark summary with competitor price range and median price
- Revenue simulation across possible price points
- Recommended launch price with reasoning
- Advisor-mode follow-up answers
- 30-day pricing test plan
- Clean visual UI with pricing cards, market snapshot, competitor table, and revenue curve

## How the Agent Works

PricePilot follows a multi-step agent workflow:

1. **User Strategy Intake**
   - The user describes the product, audience, features, and pricing goal.
   - File references: `main.py`, `src/chat_planner.py`

2. **Prompt Parsing**
   - The natural language prompt is converted into structured pricing fields.
   - File reference: `src/prompt_parser.py`

3. **Market Data Collection**
   - The agent attempts to collect live competitor pricing data from Google Shopping using SerpApi.
   - If live data is unavailable or the API key is missing, the app falls back to curated public competitor pricing data so the demo still works.
   - File references: `src/refresh_data.py`, `src/agent.py`, `src/scraper.py`

4. **Market Benchmarking**
   - The agent calculates competitor price range, median price, and positioning context.
   - File references: `src/agent.py`, `src/recommendation.py`

5. **Revenue Simulation**
   - The app simulates expected conversion, customer volume, and monthly revenue across different price points.
   - File reference: `src/simulation.py`

6. **Pricing Recommendation**
   - The agent recommends a launch price based on the user’s objective, market data, and simulated revenue.
   - File references: `src/recommendation.py`, `src/agent.py`

7. **LLM Reasoning**
   - The LLM turns the quantitative analysis into a clear pricing strategy explanation.
   - File reference: `src/llm_reasoning.py`

8. **Advisor Follow-Up**
   - Users can ask follow-up questions about pricing tests, positioning, risk, and launch strategy.
   - File references: `src/chat_planner.py`, `src/llm_reasoning.py`, `main.py`

## Project Architecture

```text
PricePilot/
│
├── main.py
│   └── FastAPI app, frontend UI, API routes
│
├── src/
│   ├── agent.py
│   │   └── Main pricing-agent orchestration
│   │
│   ├── prompt_parser.py
│   │   └── Converts user input into structured pricing context
│   │
│   ├── refresh_data.py
│   │   └── Pulls live market data when API keys are available
│   │
│   ├── scraper.py
│   │   └── Scraping / search helper logic
│   │
│   ├── build_dataset.py
│   │   └── Builds or refreshes competitor pricing data
│   │
│   ├── simulation.py
│   │   └── Revenue and demand simulation logic
│   │
│   ├── recommendation.py
│   │   └── Pricing recommendation and guardrail logic
│   │
│   ├── llm_reasoning.py
│   │   └── LLM-generated pricing explanation
│   │
│   ├── chat_planner.py
│   │   └── Advisor-style follow-up planning
│   │
│   └── benchmarking.py
│       └── Evaluation / benchmarking helpers
```

## Class Concepts Used

### 1. Agent orchestration

PricePilot is structured as an agent pipeline rather than a single prompt. The system coordinates user intake, structured parsing, market data collection, simulation, recommendation, and LLM explanation.

File references:

- `src/agent.py`
- `main.py`

### 2. Tool use and external data retrieval

The agent can use external market data from Google Shopping / SerpApi. This lets the recommendation be grounded in competitor prices instead of only relying on the LLM.

File references:

- `src/refresh_data.py`
- `src/scraper.py`
- `src/build_dataset.py`

### 3. Structured output / prompt parsing

The app converts messy user input into structured pricing fields such as product type, customer segment, positioning goal, and constraints. This makes the downstream simulation and recommendation more reliable.

File reference:

- `src/prompt_parser.py`

### 4. Simulation and decision optimization

PricePilot simulates price points and estimates expected revenue impact. This adds a quantitative layer to the agent instead of only producing generic pricing advice.

File references:

- `src/simulation.py`
- `src/recommendation.py`

### 5. LLM reasoning and explanation

The LLM is used after the quantitative analysis to explain the recommendation in plain English. This makes the product more useful for non-technical founders.

File reference:

- `src/llm_reasoning.py`

### 6. Guardrails and fallback behavior

The app includes fallback data and pricing guardrails so the demo remains stable even if live APIs fail or the LLM is unavailable.

File references:

- `src/agent.py`
- `src/llm_reasoning.py`
- `src/recommendation.py`

## Why These Technical Choices Fit the Business Case

PricePilot is built for founders and small teams who need fast, practical pricing guidance without hiring a pricing consultant.

- **Live market data** makes the recommendation more realistic.
- **Fallback data** keeps the product reliable during demos and reduces dependency on external APIs.
- **Revenue simulation** helps users compare tradeoffs between lower prices, higher conversion, and higher revenue.
- **LLM reasoning** makes the output easy to understand.
- **Advisor follow-up** makes the product feel like an interactive pricing strategist rather than a static calculator.
- **FastAPI** makes the app simple to deploy and interact with through a web interface.

## Business Model

PricePilot could be sold as a lightweight SaaS tool for founders and small ecommerce operators.

Example pricing:

- Starter: $29/month for basic pricing analyses
- Pro: $79/month for more searches, advisor follow-ups, and saved pricing plans

The cost to serve one user is relatively low because each analysis only requires a small number of search/API calls and lightweight LLM reasoning. This makes the product plausible as a subscription business if users run multiple pricing analyses per month.

## Local Setup

Clone the repo:

```bash
git clone https://github.com/jonah-ernest/PricePilot.git
cd PricePilot
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```bash
touch .env
```

Optional API keys:

```bash
SERPAPI_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
```

Run the app:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```text
http://localhost:8000
```

## Deployment

The deployed app is available here:

```text
PASTE DEPLOYED URL HERE
```

## Demo Walkthrough

1. Open the live URL.
2. Enter a product launch prompt.
3. Confirm or adjust the strategy profile.
4. Click the pricing analysis button.
5. Review the recommended launch price.
6. Show the revenue curve and competitor snapshot.
7. Ask one advisor follow-up question, such as:

```text
What pricing test should we run first?
```

or

```text
Give me a 30-day launch pricing plan.
```

## Limitations

- Competitor data quality depends on the available search results.
- The revenue simulation uses simplified elasticity assumptions, so it is best used for directional decision-making rather than exact forecasting.
- The product is strongest for early pricing strategy and launch planning, not long-term enterprise pricing optimization.
- The current version does not yet store historical experiments or user accounts.

## Future Improvements

- Save previous pricing analyses for each user
- Add product-specific elasticity assumptions
- Add A/B test sample-size recommendations
- Add competitor feature extraction from reviews
- Add exportable pricing reports
- Add team/account support for small businesses
