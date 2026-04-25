import os
from openai import OpenAI


def generate_business_explanation(category, market_summary, recommendation):
    """
    Uses an LLM if OPENAI_API_KEY is available.
    Otherwise falls back to a simple rule-based explanation.
    """

    fallback = (
        f"For {category}, competitors range from ${market_summary['min_price']} "
        f"to ${market_summary['max_price']}, with a median price of "
        f"${market_summary['median_price']}. The agent recommends "
        f"${recommendation['recommended_price']} as a {recommendation['market_position']} "
        f"price point because it produced the highest expected revenue in the simulation. "
        f"This gives the user a pricing decision based on competitor benchmarking and "
        f"demand modeling rather than guesswork."
    )

    if not os.getenv("OPENAI_API_KEY"):
        return fallback

    client = OpenAI()

    prompt = f"""
    You are a pricing strategy analyst.

    Product category: {category}

    Market summary:
    {market_summary}

    Recommendation:
    {recommendation}

    Write a concise business explanation with:
    1. pricing landscape
    2. recommended price
    3. expected revenue impact
    4. tradeoff or risk

    Keep it under 180 words.
    """

    try:
        response = client.responses.create(
            model="gpt-5.5",
            input=prompt
        )
        return response.output_text
    except Exception:
        return fallback