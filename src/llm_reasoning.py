import os

def generate_business_explanation(
    category,
    market_summary,
    recommendation,
    objective="maximize_revenue",
    question=None,
):
    question = question or "Explain the recommendation."

    fallback_answers = {
        "risk": (
            f"The main risk is that ${recommendation['recommended_price']} may be too low if the product is meant to feel premium. "
            f"It could increase conversion, but it may also reduce perceived quality or leave revenue on the table."
        ),
        "growth": (
            f"Growth pricing would likely test a lower price than ${recommendation['recommended_price']} to maximize customer volume, "
            f"even if monthly revenue per customer is lower."
        ),
        "competitor": (
            f"The most important competitors are the ones near the market median price of ${market_summary['median_price']:.2f}, "
            f"because they define what customers expect to pay."
        ),
        "discount": (
            f"A launch discount could work, but it should be temporary. Start near ${recommendation['recommended_price']} and test a limited discount "
            f"to increase early conversion without permanently weakening the price."
        ),
    }

    q = question.lower()
    if "risk" in q:
        fallback = fallback_answers["risk"]
    elif "growth" in q:
        fallback = fallback_answers["growth"]
    elif "competitor" in q:
        fallback = fallback_answers["competitor"]
    elif "discount" in q:
        fallback = fallback_answers["discount"]
    fallback = (
        f"At ${recommendation['recommended_price']}, the product is positioned below the market median of "
        f"${market_summary['median_price']:.2f}, which makes it a budget-oriented price. "
        f"That can help increase conversion because customers see it as cheaper than many alternatives. "
        f"The tradeoff is that a lower price may reduce perceived quality and leave less margin per sale. "
        f"A good next step would be to test this price against a slightly higher option, such as "
        f"${recommendation['recommended_price'] + 10:.2f}, and compare conversion and revenue."
    )

    try:
        from google import genai

        client = genai.Client()

        prompt = f"""
You are a senior pricing strategy analyst for PricePilot.

The user is asking a follow-up question about a pricing recommendation.

Product category: {category}
User question: {question}

Market data:
- Minimum competitor price: ${market_summary['min_price']}
- Median competitor price: ${market_summary['median_price']}
- Maximum competitor price: ${market_summary['max_price']}
- Number of products analyzed: {market_summary['num_products']}

Recommendation:
- Recommended price: ${recommendation['recommended_price']}
- Expected revenue: ${recommendation['expected_revenue']}
- Conversion rate: {recommendation['conversion_rate']:.2%}
- Expected customers: {recommendation['expected_customers']}
- Market position: {recommendation['market_position']}
- Objective: {objective}

Answer format:
Use this exact structure:

**Direct answer:** 1 clear sentence answering the user's question.

**Why:** 2 bullet points explaining the reasoning.

**Tradeoff:** 1 sentence explaining the downside or risk.

**Next step:** 1 concrete pricing test or action.

Rules:
- Keep it concise.
- Use bullets, not one long paragraph.
- Tie the answer to conversion, revenue, market position, or competitor prices.
- Do not use markdown headings larger than bold text.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        print("GEMINI FAILED:", e)
        return fallback
def generate_followup_suggestions(category, market_summary, recommendation, objective=None):
    price = recommendation.get("recommended_price", "the recommended price")
    position = recommendation.get("market_position", "market")

    return [
        f"What happens if I price lower than ${price}?",
        "How would premium pricing change this?",
        f"Why is this a {position} price?",
        "Should I launch with a discount?",
    ]