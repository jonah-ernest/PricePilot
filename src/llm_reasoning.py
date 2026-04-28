import os
from groq import Groq


def generate_business_explanation(category, market_summary, recommendation, question=None, objective="maximize_revenue"):
    api_key = os.getenv("GROQ_API_KEY")

    # fallback (if key missing)
    fallback = f"""
For {category}, competitors range from ${market_summary.get('min_price')} to ${market_summary.get('max_price')}, 
with a median price of ${market_summary.get('median_price')}.

The recommended price of ${recommendation.get('recommended_price')} maximizes expected revenue in the simulation.

Next step:
Run pricing experiments to validate assumptions.
"""

    if not api_key:
        return fallback

    client = Groq(api_key=api_key)

    base_context = f"""
You are an expert pricing strategy consultant.

Category: {category}

Strategic Objective: {objective}

Market Summary:
- Median price: {market_summary.get("median_price")}
- Price range: {market_summary.get("min_price")} to {market_summary.get("max_price")}
- Number of products: {market_summary.get("num_products")}

Recommendation:
- Price: {recommendation.get("recommended_price")}
- Expected revenue: {recommendation.get("expected_revenue")}
- Conversion rate: {recommendation.get("conversion_rate")}
- Position: {recommendation.get("market_position")}
"""

    if question:
        prompt = base_context + f"""

Answer like a management consultant.
Be structured, concise, and actionable.

Question:
{question}
"""
    else:
        prompt = base_context + """

Write a concise pricing strategy explanation.
Explain why this price is optimal and what it means for the business.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"[ERROR CALLING GROQ] {str(e)}"