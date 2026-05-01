import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def _extract_json(raw_text: str) -> dict:
    raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("No valid JSON found")


def _fallback_parse(user_prompt: str) -> dict:
    lower = user_prompt.lower()

    objective = "maximize_revenue"
    if any(word in lower for word in ["grow", "growth", "customers", "volume", "adoption"]):
        objective = "maximize_growth"
    elif any(word in lower for word in ["premium", "luxury", "high-end"]):
        objective = "premium_positioning"
    elif any(word in lower for word in ["competitive", "entry", "market share"]):
        objective = "competitive_entry"

    positioning = None
    if any(word in lower for word in ["budget", "cheap", "affordable", "low-cost"]):
        positioning = "budget"
    elif any(word in lower for word in ["premium", "luxury", "high-end"]):
        positioning = "premium"
    elif any(word in lower for word in ["mid", "middle", "mainstream"]):
        positioning = "mid-market"

    return {
        "product_query": user_prompt[:80],
        "business_type": None,
        "objective": objective,
        "audience": None,
        "positioning": positioning,
        "key_features": [],
        "differentiation": None,
        "customer_problem": None,
        "sales_channel": None,
        "launch_stage": "new_launch",
        "competitor_frame": None,
        "price_sensitivity": None,
        "risk_tolerance": "medium",
        "strategic_direction": None,
        "strategy_summary": None,
        "needs_clarification": True,
        "clarifying_question": "What makes this product different from the alternatives customers could buy?",
        "clarifying_questions": [
            "Who is the main customer?",
            "What makes the product stand out?",
            "Are you trying to grow quickly, maximize revenue, or position as premium?",
        ],
        "suggested_answers": [
            "Lower price than competitors",
            "Better quality for the price",
            "Designed for beginners",
            "Premium features with accessible pricing",
        ],
    }


def parse_pricing_prompt(user_prompt: str) -> dict:
    if not client:
        return _fallback_parse(user_prompt)

    prompt = f"""
You are the strategy discovery brain for PricePilot, an AI pricing strategy agent.

Your job is to read the full conversation and decide whether the agent has enough strategic context to build a useful pricing dashboard.

Conversation:
{user_prompt}

Return ONLY valid JSON with this exact structure:
{{
  "product_query": "short product search phrase for Google Shopping",
  "business_type": "type of business or null",
  "objective": "maximize_revenue | maximize_growth | competitive_entry | premium_positioning",
  "audience": "target customer or null",
  "positioning": "budget | mid-market | premium | null",
  "key_features": ["feature 1", "feature 2"],
  "differentiation": "why the product is different or null",
  "customer_problem": "customer pain point being solved or null",
  "sales_channel": "online store | retail | marketplace | subscription | direct sales | null",
  "launch_stage": "new_launch | existing_product | repositioning | null",
  "competitor_frame": "who the product should be compared against or null",
  "price_sensitivity": "low | medium | high | null",
  "risk_tolerance": "low | medium | high | null",
  "strategic_direction": "short strategy label",
  "strategy_summary": "2 sentence summary of how you understand the product strategy",
  "needs_clarification": true,
  "clarifying_question": "single best follow-up question or null",
  "clarifying_questions": ["question 1", "question 2", "question 3"],
  "suggested_answers": ["option 1", "option 2", "option 3", "option 4"]
}}

Decision rules:
- If no product is mentioned, needs_clarification must be true.
- If the user only gave a product category, needs_clarification must be true.
- If the user gave product, audience, pricing goal or positioning, and at least one feature or differentiator, needs_clarification should usually be false.
- Do not ask endless questions.
- After 1 or 2 useful user answers, prefer needs_clarification=false.
- Ask only ONE main clarifying_question.
- The next question should feel like a pricing strategist, not a form.
- Suggested answers must be short, clickable button-style options.
- product_query must be broad enough for Google Shopping search.
- strategy_summary should sound like an analyst summarizing the product strategy.
- Return only JSON. No markdown. No explanation.

Question selection rules:
- If target customer is missing, ask who the product is for.
- If differentiation is missing, ask why customers would choose this over alternatives.
- If pricing objective is unclear, ask whether the user wants growth, revenue, competitive entry, or premium positioning.
- If sales channel is missing but the rest is complete, do not block the dashboard. Infer "online store" when reasonable.
- If launch stage is missing but the rest is complete, do not block the dashboard. Infer "new_launch" when reasonable.
- If enough context exists, set needs_clarification=false.

Example 1:

Conversation:
User: I am launching a new specialized electronics store focused on DJ equipment. My third product I need your help for is turntables.
Agent: What features or benefits will make your turntables appealing to DJs?
User: High-torque motor for smooth playback.
Agent: What pricing objective are you targeting with your turntables, such as maximizing revenue or competitive entry?
User: Budget-friendly option for beginners.

Output:
{{
  "product_query": "DJ turntables",
  "business_type": "specialized electronics store",
  "objective": "competitive_entry",
  "audience": "beginner DJs",
  "positioning": "budget",
  "key_features": ["high-torque motor", "smooth playback"],
  "differentiation": "budget-friendly beginner turntable with smooth playback",
  "customer_problem": "beginner DJs need reliable equipment without paying professional prices",
  "sales_channel": "online store",
  "launch_stage": "new_launch",
  "competitor_frame": "entry-level DJ turntables",
  "price_sensitivity": "high",
  "risk_tolerance": "medium",
  "strategic_direction": "Budget-friendly competitive entry",
  "strategy_summary": "This looks like a budget-friendly entry product for beginner DJs. The best strategy is to stay accessible on price while using the high-torque motor as proof that the product is still credible and reliable.",
  "needs_clarification": false,
  "clarifying_question": null,
  "clarifying_questions": [],
  "suggested_answers": []
}}

Example 2:

Conversation:
User: I sell a budget standing desk for remote workers. What price helps me grow fast?

Output:
{{
  "product_query": "standing desk",
  "business_type": null,
  "objective": "maximize_growth",
  "audience": "remote workers",
  "positioning": "budget",
  "key_features": [],
  "differentiation": null,
  "customer_problem": "remote workers need affordable ergonomic home office equipment",
  "sales_channel": "online store",
  "launch_stage": "new_launch",
  "competitor_frame": "budget standing desks",
  "price_sensitivity": "high",
  "risk_tolerance": "medium",
  "strategic_direction": "Growth-focused budget entry",
  "strategy_summary": "This looks like a budget standing desk for remote workers where the goal is fast adoption. The pricing strategy should prioritize conversion and accessibility over maximum margin.",
  "needs_clarification": true,
  "clarifying_question": "What makes your standing desk appealing enough for remote workers to choose it over other budget options?",
  "clarifying_questions": [
    "What features make it stand out?",
    "Where will you sell it?",
    "Are you competing mostly on price, quality, or convenience?"
  ],
  "suggested_answers": [
    "Compact for small apartments",
    "Easy to assemble",
    "Adjustable ergonomic height",
    "Durable but lower-cost than premium brands"
  ]
}}

Example 3:

Conversation:
User: I sell a budget standing desk for remote workers. What price helps me grow fast?
Agent: What makes your standing desk appealing enough for remote workers to choose it over other budget options?
User: Compact for small apartments, easy to assemble, and adjustable ergonomic height.

Output:
{{
  "product_query": "standing desk",
  "business_type": null,
  "objective": "maximize_growth",
  "audience": "remote workers",
  "positioning": "budget",
  "key_features": ["compact for small apartments", "easy to assemble", "adjustable ergonomic height"],
  "differentiation": "compact and easy-to-assemble ergonomic desk for remote workers in small spaces",
  "customer_problem": "remote workers need affordable ergonomic equipment that fits smaller homes",
  "sales_channel": "online store",
  "launch_stage": "new_launch",
  "competitor_frame": "budget standing desks",
  "price_sensitivity": "high",
  "risk_tolerance": "medium",
  "strategic_direction": "Growth-focused budget entry",
  "strategy_summary": "This looks like a compact budget standing desk for remote workers with limited space. The strongest strategy is to price for growth while emphasizing convenience, ergonomics, and easy setup.",
  "needs_clarification": false,
  "clarifying_question": null,
  "clarifying_questions": [],
  "suggested_answers": []
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()

    try:
        parsed = _extract_json(raw)
    except Exception:
        return _fallback_parse(user_prompt)

    defaults = {
        "product_query": "",
        "business_type": None,
        "objective": "maximize_revenue",
        "audience": None,
        "positioning": None,
        "key_features": [],
        "differentiation": None,
        "customer_problem": None,
        "sales_channel": None,
        "launch_stage": None,
        "competitor_frame": None,
        "price_sensitivity": None,
        "risk_tolerance": "medium",
        "strategic_direction": None,
        "strategy_summary": None,
        "needs_clarification": True,
        "clarifying_question": "Can you tell me what makes this product different from competitors?",
        "clarifying_questions": [],
        "suggested_answers": [],
    }

    for key, value in defaults.items():
        parsed.setdefault(key, value)

    if parsed["key_features"] is None:
        parsed["key_features"] = []

    if parsed["clarifying_questions"] is None:
        parsed["clarifying_questions"] = []

    if parsed["suggested_answers"] is None:
        parsed["suggested_answers"] = []

    return parsed