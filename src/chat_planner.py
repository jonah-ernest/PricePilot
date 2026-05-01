def _has(value):
    if value is None:
        return False
    if isinstance(value, list):
        return len([v for v in value if str(v).strip()]) > 0
    return str(value).strip() != "" and str(value).lower() != "null"


def _clean(value, fallback="not specified"):
    if not _has(value):
        return fallback
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if str(v).strip())
    return str(value)


def _objective_explicit(raw_context):
    lower = raw_context.lower()
    keywords = [
        "growth",
        "grow",
        "adoption",
        "customers",
        "market share",
        "maximize revenue",
        "revenue",
        "profit",
        "premium",
        "luxury",
        "high-end",
        "competitive",
        "entry",
        "undercut",
    ]
    return any(word in lower for word in keywords)


def _context_summary(profile):
    bits = []

    if _has(profile.get("product_query")):
        bits.append(f"product: {_clean(profile.get('product_query'))}")

    if _has(profile.get("audience")):
        bits.append(f"customer: {_clean(profile.get('audience'))}")

    if _has(profile.get("positioning")):
        bits.append(f"positioning: {_clean(profile.get('positioning'))}")

    if _has(profile.get("key_features")):
        bits.append(f"edge: {_clean(profile.get('key_features'))}")

    if not bits:
        return "I’m still building the product profile."

    return "So far I understand the " + "; ".join(bits) + "."


def _question_for_phase(phase, profile):
    product = _clean(profile.get("product_query"), "this product")
    audience = _clean(profile.get("audience"), "your target customer")

    questions = {
        "product": "What product are you trying to price?",
        "audience": f"Who is the first customer segment you most want to win for {product}?",
        "positioning": f"How do you want {audience} to perceive {product} in the market?",
        "differentiation": f"Why would {audience} choose your {product} over the alternatives?",
        "objective": "What is the main pricing goal for this launch?",
    }

    return questions.get(phase, "What else should I know before building the pricing strategy?")


def _chips_for_phase(phase, profile):
    product = _clean(profile.get("product_query"), "this product")

    if phase == "product":
        return [
            "Wireless headphones",
            "Standing desk",
            "DJ turntables",
            "Skincare product",
        ]

    if phase == "audience":
        return [
            "Beginners / first-time buyers",
            "Budget-conscious shoppers",
            "Professionals / power users",
            "Enthusiasts who care about quality",
        ]

    if phase == "positioning":
        return [
            "Budget-friendly entry option",
            "Best value for the price",
            "Premium but still accessible",
            "High-end specialist product",
        ]

    if phase == "differentiation":
        return [
            "Lower price than competitors",
            "Better quality for the price",
            "Easier to use than alternatives",
            "Specialized for this customer segment",
        ]

    if phase == "objective":
        return [
            "Grow quickly",
            "Maximize revenue",
            "Enter competitively",
            "Signal premium quality",
        ]

    return [
        f"Recommend the best strategy for {product}",
        "I am not sure yet",
    ]


def determine_next_phase(profile, raw_context):
    if not _has(profile.get("product_query")):
        return "product"

    if not _has(profile.get("audience")):
        return "audience"

    if not _has(profile.get("positioning")):
        return "positioning"

    has_features = _has(profile.get("key_features"))
    has_differentiation = _has(profile.get("differentiation"))

    if not has_features and not has_differentiation:
        return "differentiation"

    if not _objective_explicit(raw_context):
        return "objective"

    return None


def strategy_ready(profile, raw_context):
    return determine_next_phase(profile, raw_context) is None


def plan_next_discovery_turn(profile, raw_context):
    phase = determine_next_phase(profile, raw_context)

    if phase is None:
        return {
            "needs_clarification": False,
            "chat_phase": "ready",
            "clarifying_question": None,
            "suggested_answers": [],
        }

    context = _context_summary(profile)
    question = _question_for_phase(phase, profile)

    message = (
        f"{context}\n\n"
        f"To make the pricing recommendation more strategic, I need one more decision:\n\n"
        f"**{question}**"
    )

    return {
        "needs_clarification": True,
        "chat_phase": phase,
        "clarifying_question": message,
        "suggested_answers": _chips_for_phase(phase, profile),
    }