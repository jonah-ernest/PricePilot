import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def parse_pricing_prompt(user_prompt: str) -> dict:
    prompt = f"""
You are helping a pricing strategy agent understand a user's request.

Extract structured information from the user prompt.

User prompt:
{user_prompt}

Return ONLY valid JSON with these fields:
{{
  "product_query": "short product search phrase for Google Shopping",
  "objective": "maximize_revenue | maximize_growth | competitive_entry | premium_positioning",
  "audience": "target customer or null",
  "positioning": "budget | mid-market | premium | null",
  "needs_clarification": false,
  "clarifying_question": null,
  "clarifying_questions": []
}}

Examples:

User prompt:
"I'm launching wireless headphones for commuters. What price should I charge?"
Output:
{{
  "product_query": "wireless headphones",
  "objective": "maximize_revenue",
  "audience": "commuters",
  "positioning": "mid-market",
  "needs_clarification": false,
  "clarifying_question": null,
  "clarifying_questions": [
    "What is your cost per unit?",
    "What makes your headphones different from competitors?"
  ]
}}

User prompt:
"I sell premium skincare and want to position it as luxury."
Output:
{{
  "product_query": "skincare",
  "objective": "premium_positioning",
  "audience": null,
  "positioning": "premium",
  "needs_clarification": false,
  "clarifying_question": null,
  "clarifying_questions": [
    "Who is your target customer?",
    "What is your expected cost per unit?"
  ]
}}

User prompt:
"What should I charge?"
Output:
{{
  "product_query": "",
  "objective": "maximize_revenue",
  "audience": null,
  "positioning": null,
  "needs_clarification": true,
  "clarifying_question": "What product are you trying to price?",
  "clarifying_questions": []
}}

Rules:
- Return only valid JSON. No markdown. No explanation.
- product_query must be only the product/category, not the full question.
- If a concrete product is mentioned, needs_clarification must be false.
- If no product is mentioned, needs_clarification must be true.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except Exception:
        # Safe fallback (prevents broken UI + bad queries)
        return {
            "product_query": "",
            "objective": "maximize_revenue",
            "audience": None,
            "positioning": None,
            "needs_clarification": True,
            "clarifying_question": "What product are you trying to price?",
            "clarifying_questions": [],
        }