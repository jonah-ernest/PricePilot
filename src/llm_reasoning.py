import os
import re
from google import genai


def get_gemini_client():
    if not os.getenv("GEMINI_API_KEY"):
        return None
    return genai.Client()


def clean_llm_text(text):
    if not text:
        return ""

    text = text.replace("* ", "• ")
    text = re.sub(r"\n-\s+", "\n• ", text)

    return text.strip()


def generate_business_explanation(
    category,
    market_summary,
    recommendation,
    objective="maximize_revenue",
    question=None,
):
    question = question or "Explain the recommendation."

    recommended_price = recommendation["recommended_price"]
    median_price = market_summary["median_price"]
    market_position = recommendation["market_position"]

    if objective == "maximize_growth":
        fallback = (
            f"Direct answer: ${recommended_price} is recommended because it is optimized for customer growth, not maximum revenue.\n\n"
            f"Why:\n"
            f"• The lower price supports a higher conversion rate of {recommendation['conversion_rate']:.2%}.\n"
            f"• It is positioned as a {market_position} option compared with the market median of ${median_price:.2f}.\n\n"
            f"Tradeoff: A higher price may produce more revenue per sale, but it could reduce customer volume.\n\n"
            f"Next step: Test ${recommended_price} against a slightly higher price to compare growth and revenue."
        )
    elif objective == "premium_positioning":
        fallback = (
            f"Direct answer: ${recommended_price} is recommended because it supports a premium market position.\n\n"
            f"Why:\n"
            f"• The price is above the market median of ${median_price:.2f}.\n"
            f"• Premium pricing can support stronger margins and brand positioning.\n\n"
            f"Tradeoff: A higher price may reduce conversion among budget-conscious buyers.\n\n"
            f"Next step: Test this price against a mid-market option to measure conversion loss."
        )
    elif objective == "competitive_entry":
        fallback = (
            f"Direct answer: ${recommended_price} is recommended as an entry price below the market median.\n\n"
            f"Why:\n"
            f"• It positions the product below the median competitor price of ${median_price:.2f}.\n"
            f"• This can help attract customers who are comparing similar products.\n\n"
            f"Tradeoff: Entering too low may make the product feel less premium.\n\n"
            f"Next step: Test this price against the market median to compare conversion and revenue."
        )
    else:
        fallback = (
            f"Direct answer: ${recommended_price} is recommended because it has the strongest expected revenue in the simulation.\n\n"
            f"Why:\n"
            f"• It is expected to generate ${recommendation['expected_revenue']} per month.\n"
            f"• It balances price and conversion at an estimated {recommendation['conversion_rate']:.2%} conversion rate.\n\n"
            f"Tradeoff: This price may not maximize customer count if a lower growth-focused price is used.\n\n"
            f"Next step: Test this price against nearby prices to validate the revenue estimate."
        )

    try:
        client = get_gemini_client()
        if not client:
            return fallback

        prompt = f"""
You are a senior pricing strategy analyst for PricePilot.

The user is asking about a pricing recommendation.

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

Critical instruction:
- If objective is maximize_growth, explain that this price is optimized for customer growth and conversion, NOT maximum revenue.
- If objective is maximize_revenue, explain that this price is optimized for expected revenue.
- If objective is premium_positioning, explain that this price is optimized for premium positioning and margin.
- If objective is competitive_entry, explain that this price is optimized for entering below the market median.
- Do NOT claim this is the highest revenue price unless objective is maximize_revenue.
- Do NOT say "maximize revenue" when objective is maximize_growth.

Use this exact answer structure:

**Direct answer:** 1 clear sentence.

**Why:**
- First reason.
- Second reason.

**Tradeoff:** 1 sentence.

**Next step:** 1 concrete pricing test or action.

Rules:
- Keep it concise.
- Use markdown bold for the labels only.
- Use dash bullets only under Why.
- Tie the answer to the selected objective.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return clean_llm_text(response.text)

    except Exception:
        return fallback


def generate_followup_suggestions(category, market_summary, recommendation, objective=None):
    price = recommendation.get("recommended_price", "the recommended price")
    position = recommendation.get("market_position", "market")

    if objective == "maximize_growth":
        return [
            f"Why does ${price} maximize growth?",
            "What price would maximize revenue instead?",
            f"Why is this a {position} price?",
            "Should I launch with a discount?",
        ]

    return [
        f"What happens if I price lower than ${price}?",
        "How would premium pricing change this?",
        f"Why is this a {position} price?",
        "Should I launch with a discount?",
    ]