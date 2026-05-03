# PricePilot

PricePilot is an AI pricing strategy agent that helps founders and small ecommerce teams choose a launch price using competitor market data, revenue simulation, and LLM-based pricing strategy explanations.

## Live Demo

Live URL: 

## What It Does

1. Collects a product strategy profile through a chatbot-style flow.
2. Pulls live Google Shopping competitor data when available.
3. Falls back to curated demo competitor data if live search is unavailable.
4. Computes market pricing benchmarks.
5. Simulates price, conversion, customer volume, and expected monthly revenue.
6. Recommends a launch price based on the user’s goal.
7. Lets the user pressure-test the strategy with advisor-mode follow-up questions.

## How to Run Locally

```bash
git clone https://github.com/jonah-ernest/PricePilot.git
cd PricePilot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
