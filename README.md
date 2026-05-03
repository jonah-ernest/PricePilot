# PricePilot

PricePilot is an AI pricing strategy agent that helps founders and small ecommerce teams choose a launch price using competitor market data, revenue simulation, and LLM-based pricing reasoning.

Instead of forcing users to manually search competitor prices and guess a price point, PricePilot combines market benchmarking, pricing simulation, guardrailed recommendation logic, and advisor-style follow-up questions into one workflow.

## Live Demo

Live URL:

## Product Overview

PricePilot is designed for early-stage founders, ecommerce sellers, and small product teams who are preparing to launch or reposition a product.

The agent helps answer questions like:

- What price should I launch at?
- Am I underpriced or overpriced compared to competitors?
- What happens to revenue if I raise or lower price?
- Should I optimize for growth, revenue, or premium positioning?
- What pricing experiment should I run next?

## Key Features

- Chatbot-style pricing strategy intake
- Structured parsing of the user’s product, audience, positioning, and pricing goal
- Live competitor price lookup using Google Shopping / SerpApi when available
- Market benchmark summary with competitor price range and median price
- Revenue simulation across possible price points
- Objective-based launch price recommendation
- Guardrails for cost floors and premium positioning
- LLM-generated explanation of the recommendation
- Advisor-mode follow-up answers
- 30-day pricing test plan
- Visual UI with pricing cards, market snapshot, competitor table, and revenue curve

## How the Agent Works

PricePilot follows a multi-step agent workflow:

1. **User Strategy Intake**
   - The user describes the product, target audience, features, and pricing goal.
   - File reference: `main.py`

2. **Prompt Parsing**
   - The natural language prompt is converted into structured pricing fields.
   - File reference: `src/prompt_parser.py`

3. **Market Data Collection**
   - The agent attempts to collect live competitor pricing data from Google Shopping using SerpApi.
   - If live data is unavailable or the API key is missing, the app falls back to curated public competitor pricing data so the demo still works.
   - File references: `src/refresh_data.py`, `src/agent.py`, `src/scraper.py`

4. **Market Benchmarking**
   - The agent calculates competitor price range, median price, average price, product count, ratings, and review context.
   - File references: `src/benchmarking.py`, `src/agent.py`

5. **Revenue Simulation**
   - The app simulates expected conversion, customer volume, and monthly revenue across different price points.
   - File reference: `src/simulation.py`

6. **Pricing Recommendation**
   - The agent recommends a launch price based on the user’s objective, market data, simulated revenue, and guardrails.
   - File references: `src/recommendation.py`, `src/agent.py`

7. **LLM Reasoning**
   - The LLM turns the quantitative analysis into a clear pricing strategy explanation.
   - File reference: `src/llm_reasoning.py`

8. **Advisor Follow-Up**
   - Users can ask follow-up questions about pricing tests, positioning, risk, launch strategy, and 30-day plans.
   - File references: `main.py`, `src/llm_reasoning.py`

## Project Architecture

```text
PricePilot/
│
├── main.py
│   └── FastAPI app, frontend UI, API routes, chatbot/advisor flow
│
├── src/
│   ├── agent.py
│   │   └── Main pricing-agent orchestration
│   │
│   ├── prompt_parser.py
│   │   └── Converts user input into structured pricing context
│   │
│   ├── refresh_data.py
│   │   └── Pulls live Google Shopping market data when API keys are available
│   │
│   ├── scraper.py
│   │   └── Curated fallback competitor pricing data
│   │
│   ├── benchmarking.py
│   │   └── Market summary statistics and competitor benchmarks
│   │
│   ├── simulation.py
│   │   └── Revenue and demand simulation logic
│   │
│   ├── recommendation.py
│   │   └── Objective-based pricing recommendation logic
│   │
│   └── llm_reasoning.py
│       └── LLM-generated pricing explanation and advisor responses
```

## Class Concepts Used

### 1. Agent orchestration / agent loop

PricePilot uses an agent-style workflow instead of a single LLM prompt. The main orchestration happens in `run_pricing_agent()`, which coordinates parsing, data retrieval, benchmarking, simulation, recommendation, guardrails, and LLM explanation.

File references:

- `src/agent.py` — main agent workflow in `run_pricing_agent()`
- `main.py` — FastAPI app and user-facing chatbot flow

### 2. Agents as functions inside a web app

The pricing agent is implemented as a callable backend workflow and exposed through FastAPI routes. This follows the class idea that an agent can be treated as a function inside a larger application: input comes from the UI, the backend runs the agent workflow, and the result is returned to the user.

File references:

- `main.py` — web server, API routes, and UI
- `src/agent.py` — callable pricing-agent workflow

### 3. Tool calling / external data retrieval

PricePilot uses external data-retrieval functions to ground its recommendations in market data. The agent attempts to fetch live Google Shopping competitor data through SerpApi and falls back to curated competitor pricing data when live data is unavailable.

File references:

- `src/refresh_data.py` — live Google Shopping / SerpApi retrieval
- `src/scraper.py` — curated fallback competitor pricing data
- `src/agent.py` — chooses live data or fallback data

### 4. Structured output / constrained parsing

PricePilot converts messy natural-language user input into structured pricing fields before running the analysis. The parser extracts fields such as product query, pricing objective, audience, positioning, key features, sales channel, launch stage, price sensitivity, and risk tolerance.

This is not full token-level constrained decoding, but it uses structured JSON-style output and fallback parsing to make the rest of the workflow more reliable.

File reference:

- `src/prompt_parser.py` — `parse_pricing_prompt()`

### 5. Prompt and context engineering

The LLM explanation step uses a structured prompt with a clear role, market context, recommendation data, objective-specific rules, and required response sections. This keeps the final explanation tied to the actual pricing analysis instead of producing generic business advice.

The prompts mostly use positive formatting constraints, such as required sections and concise answer structure, while using a few negative constraints for important business-safety cases, such as preventing the model from calling a growth-optimized price a revenue-maximizing price.

File reference:

- `src/llm_reasoning.py` — `generate_business_explanation()` and advisor response logic

### 6. Guardrails and fallback behavior

PricePilot includes rule-based guardrails to make recommendations safer and more business-realistic. For example, if the user gives a cost floor, the agent prevents the recommended price from going below that minimum. The app also includes fallback data and fallback explanations so the demo remains reliable if an API key is missing or an external service fails.

File references:

- `src/agent.py` — cost-floor and recommendation guardrails
- `src/llm_reasoning.py` — fallback explanation text
- `src/scraper.py` — fallback competitor data

### 7. Simulation, benchmarking, and evaluation mindset

PricePilot does not rely only on LLM advice. It computes market benchmarks, simulates prices across a demand curve, and compares expected customers and expected revenue across price points. This turns the agent into an analytics workflow rather than a generic chatbot.

File references:

- `src/benchmarking.py` — market summary statistics
- `src/simulation.py` — revenue and conversion simulation
- `src/recommendation.py` — objective-based price selection

## Why These Technical Choices Fit the Business Case

PricePilot is built for founders and small teams who need fast, practical pricing guidance without hiring a pricing consultant.

- **Live market data** makes the recommendation more realistic.
- **Structured parsing** turns vague founder input into fields the pricing workflow can use.
- **Revenue simulation** helps users compare tradeoffs between lower prices, higher conversion, and higher revenue.
- **Objective-based recommendation logic** lets the agent adapt to different pricing goals, such as growth, revenue, competitive entry, or premium positioning.
- **Guardrails** prevent unrealistic recommendations, such as pricing below a user-provided cost floor.
- **LLM reasoning** makes the output easy to understand for non-technical users.
- **Advisor follow-up** makes the product feel like an interactive pricing strategist rather than a static calculator.
- **FastAPI** makes the app simple to deploy and interact with through a web interface.

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
## Future Improvements

- Save previous pricing analyses for each user
- Add product-specific elasticity assumptions
- Add A/B test sample-size recommendations
- Add competitor feature extraction from reviews
- Add exportable pricing reports
- Add team/account support for small businesses
- Add historical experiment tracking so users can compare predicted vs. actual pricing results
