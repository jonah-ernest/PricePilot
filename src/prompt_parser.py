import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def _extract_json(raw_text: str) -> dict:
    raw_text = str(raw_text or "").strip()

    try:
        return json.loads(raw_text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("No valid JSON found")


def _fallback_parse(user_prompt: str) -> dict:
    text = str(user_prompt or "").strip()
    lower = text.lower()

    objective = "maximize_revenue"
    if any(word in lower for word in ["grow", "growth", "customers", "volume", "adoption"]):
        objective = "maximize_growth"
    elif any(word in lower for word in ["premium", "luxury", "high-end", "high end"]):
        objective = "premium_positioning"
    elif any(word in lower for word in ["competitive", "entry", "market share", "undercut"]):
        objective = "competitive_entry"
    elif any(word in lower for word in ["revenue", "profit", "margin"]):
        objective = "maximize_revenue"

    positioning = None
    if any(word in lower for word in ["budget", "cheap", "affordable", "low-cost", "low cost"]):
        positioning = "budget"
    elif any(word in lower for word in ["premium", "luxury", "high-end", "high end"]):
        positioning = "premium"
    elif any(word in lower for word in ["mid", "middle", "mainstream", "value"]):
        positioning = "mid-market"

    product_query = text[:80] if text else ""

    return {
        "product_query": product_query,
        "business_type": None,
        "objective": objective,
        "audience": None,
        "positioning": positioning,
        "key_features": [],
        "differentiation": None,
        "customer_problem": None,
        "sales_channel": "online store",
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

def render_quick_actions(result, profile, phase, history, session_id):
    if phase != "complete" or not result:
        return ""

    questions = post_analysis_questions(result)

    profile_value = encode_json(profile)
    history_value = encode_json(history)

    buttons = ""
    for question in questions:
        buttons += f"""
        <form method="post" action="/chat">
          <input type="hidden" name="message" value="{safe_text(question)}">
          <input type="hidden" name="profile" value="{profile_value}">
          <input type="hidden" name="phase" value="{safe_text(phase)}">
          <input type="hidden" name="history" value="{history_value}">
          <input type="hidden" name="session_id" value="{safe_text(session_id)}">
          <button class="quick-action-chip" type="submit">{safe_text(question)}</button>
        </form>
        """

    return f"""
    <div class="quick-actions-sticky">
      <div class="quick-actions-title">Try next</div>
      <div class="quick-actions-row">
        {buttons}
      </div>
    </div>
    """
    
def _normalize_parsed(parsed: dict, user_prompt: str) -> dict:
    fallback = _fallback_parse(user_prompt)

    defaults = {
        "product_query": fallback["product_query"],
        "business_type": None,
        "objective": "maximize_revenue",
        "audience": None,
        "positioning": None,
        "key_features": [],
        "differentiation": None,
        "customer_problem": None,
        "sales_channel": "online store",
        "launch_stage": "new_launch",
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

    if not isinstance(parsed, dict):
        parsed = {}

    for key, value in defaults.items():
        parsed.setdefault(key, value)

    if not parsed.get("product_query"):
        parsed["product_query"] = fallback["product_query"]

    if parsed.get("key_features") is None:
        parsed["key_features"] = []

    if parsed.get("clarifying_questions") is None:
        parsed["clarifying_questions"] = []

    if parsed.get("suggested_answers") is None:
        parsed["suggested_answers"] = []

    if parsed.get("objective") not in [
        "maximize_revenue",
        "maximize_growth",
        "competitive_entry",
        "premium_positioning",
    ]:
        parsed["objective"] = fallback["objective"]

    if parsed.get("positioning") not in ["budget", "mid-market", "premium", None]:
        parsed["positioning"] = fallback["positioning"]

    return parsed


def parse_pricing_prompt(user_prompt: str) -> dict:
    if not client:
        return _fallback_parse(user_prompt)

    prompt = f"""
You are the strategy discovery brain for PricePilot, an AI pricing strategy agent.

Read the conversation and return ONLY valid JSON.

Conversation:
{user_prompt}

Return this exact JSON structure:
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
  "strategy_summary": "2 sentence summary of the product strategy",
  "needs_clarification": true,
  "clarifying_question": "single best follow-up question or null",
  "clarifying_questions": ["question 1", "question 2", "question 3"],
  "suggested_answers": ["option 1", "option 2", "option 3", "option 4"]
}}

Rules:
- If only a product category is given, needs_clarification should be true.
- If product, audience, positioning or pricing goal, and differentiation are present, needs_clarification should usually be false.
- Do not ask endless questions.
- product_query should be broad enough for shopping search.
- If sales_channel is missing but the rest is usable, infer "online store".
- If launch_stage is missing but the rest is usable, infer "new_launch".
- Return only JSON. No markdown.
"""

    try:
        messages = [
            {
                "role": "system",
                "content": "You convert pricing strategy conversations into strict JSON.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0,
        )

        raw = response.choices[0].message.content.strip()
        parsed = _extract_json(raw)
        return _normalize_parsed(parsed, user_prompt)

    except Exception as e:
        print(f"LLM prompt parsing failed, using fallback parser: {e}")
        return _fallback_parse(user_prompt)