import os
import sys
import html
import json
import uuid
import re
import markdown

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from src.agent import run_pricing_agent
from src.prompt_parser import parse_pricing_prompt
from src.llm_reasoning import (
    generate_business_explanation,
    generate_followup_questions_after_analysis,
)

app = FastAPI(title="PricePilot")

RESULT_CACHE = {}

STYLE = """
<style>
:root {
  --bg: #f7fbff;
  --panel: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: #dbeafe;
  --accent: #0284c7;
  --accent-dark: #0369a1;
  --soft: #e0f2fe;
  --success: #16a34a;
  --warning: #f59e0b;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
}

.topbar {
  height: 76px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 28px;
  border-bottom: 1px solid var(--border);
  background: white;
}

.logo {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--accent);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
}

.topbar h1 {
  font-size: 21px;
  margin: 0;
}

.topbar p {
  margin: 2px 0 0;
  color: var(--muted);
}

.layout {
  display: grid;
  grid-template-columns: 42% 58%;
  min-height: calc(100vh - 76px);
}

.chat {
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 76px);
  background: #f8fbff;
}

.messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.msg-row {
  display: flex;
  margin-bottom: 16px;
}

.msg-row.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 86%;
  padding: 15px 17px;
  border-radius: 18px;
  line-height: 1.45;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
  font-size: 15px;
}

.user .bubble {
  background: var(--accent);
  color: white;
  border-bottom-right-radius: 6px;
}

.agent .bubble {
  background: white;
  border: 1px solid var(--border);
  border-bottom-left-radius: 6px;
}

.agent-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  flex-shrink: 0;
  font-size: 14px;
}

.setup-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.setup-title {
  font-weight: 800;
  margin-bottom: 8px;
}

.progress-track {
  height: 8px;
  background: #e5f3ff;
  border-radius: 999px;
  overflow: hidden;
  margin: 8px 0 12px;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 999px;
}

.progress-steps {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
  font-size: 11px;
  color: var(--muted);
}

.step.done {
  color: var(--success);
  font-weight: 800;
}

.input-area {
  padding: 18px;
  border-top: 1px solid var(--border);
  background: white;
}

.input-form {
  display: flex;
  gap: 10px;
}

input[type="text"] {
  width: 100%;
  padding: 15px 16px;
  border: 1px solid var(--border);
  border-radius: 18px;
  font-size: 16px;
  outline: none;
}

button {
  border: none;
  background: var(--accent);
  color: white;
  padding: 13px 18px;
  border-radius: 16px;
  font-weight: 750;
  cursor: pointer;
}

button:hover {
  background: var(--accent-dark);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin: 6px 0 18px 42px;
}

.chip {
  background: white;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 9px 13px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
  cursor: pointer;
  font-size: 13px;
}

.chip.primary-chip {
  background: var(--accent);
  color: white;
}

.chip:hover {
  background: var(--soft);
  color: var(--text);
}

.dashboard {
  padding: 24px;
  overflow-y: auto;
}

.card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 18px;
  margin-bottom: 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.card h2,
.card h3 {
  margin-top: 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.metric {
  background: #f8fafc;
  border-radius: 16px;
  padding: 14px;
}

.metric-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.metric-value {
  font-size: 23px;
  font-weight: 850;
  margin-top: 5px;
}

.small {
  color: var(--muted);
  font-size: 12px;
}

.canvas-row {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}

.canvas-row:last-child {
  border-bottom: none;
}

.canvas-label {
  color: var(--muted);
  font-weight: 750;
}

.canvas-value {
  font-weight: 650;
}

.empty-value {
  color: #94a3b8;
  font-weight: 500;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th,
.table td {
  padding: 8px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

.bars {
  display: flex;
  align-items: end;
  gap: 7px;
  height: 150px;
  margin-top: 14px;
}

.bar-wrap {
  flex: 1;
  text-align: center;
  font-size: 10px;
  color: var(--muted);
}

.bar {
  width: 100%;
  background: #bae6fd;
  border-radius: 8px 8px 0 0;
}

.bar.best {
  background: var(--accent);
}

.confirm-box {
  background: #eff6ff;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  margin-top: 8px;
}

/* --- Chat polish overrides --- */

.messages {
  padding: 20px 22px 120px;
}

.bubble {
  font-size: 14px;
}

.user .bubble {
  max-width: 62%;
}

.agent .bubble {
  max-width: 74%;
}

.msg-row {
  margin-bottom: 14px;
}

.setup-card {
  position: sticky;
  top: 0;
  z-index: 5;
}

.advisor-actions {
  margin: 10px 0 20px 42px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.advisor-actions form {
  margin: 0;
}

.action-chip {
  width: 100%;
  border-radius: 14px;
  text-align: left;
  padding: 12px 14px;
  background: #ffffff;
  border: 1px solid var(--border);
  color: var(--text);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
}

.action-chip:hover {
  background: var(--soft);
}

.action-chip.primary-chip {
  background: var(--accent);
  color: white;
}

.advisor-label {
  font-size: 11px;
  color: var(--muted);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 6px;
}

/* --- Advisor workspace polish --- */

.chips.advisor-actions {
  margin: 12px 0 20px 42px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.action-group-title {
  grid-column: 1 / -1;
  font-size: 11px;
  color: var(--muted);
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 4px;
}

.chips.advisor-actions form {
  margin: 0;
}

.action-chip {
  width: 100%;
  border-radius: 14px;
  text-align: left;
  padding: 12px 14px;
  background: #ffffff;
  border: 1px solid var(--border);
  color: var(--text);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
}

.action-chip:hover {
  background: var(--soft);
}

.action-chip.primary-chip {
  background: var(--accent);
  color: white;
}

.chat-archive-note {
  margin: 0 0 14px 42px;
  color: var(--muted);
  font-size: 12px;
}

.active-plan-card {
  border: 1px solid #bae6fd;
  background: #f0f9ff;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 11px;
  margin-top: 12px;
}

.plan-box {
  background: white;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 13px;
}

.plan-box-title {
  font-size: 12px;
  color: var(--muted);
  font-weight: 800;
  margin-bottom: 5px;
}

/* --- Compact Advisor Mode layout --- */

.recent-discussion-title {
  margin: 16px 0 8px 42px;
  font-size: 11px;
  color: var(--muted);
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.advisor-spacer {
  height: 8px;
}

.chat-archive-note {
  margin: 8px 0 12px 42px;
  color: var(--muted);
  font-size: 12px;
}

/* Keeps the full app from becoming one giant page scroll */
html,
body {
    height: 100%;
    margin: 0;
    overflow: hidden;
}

/* Header stays visible at the top */
.topbar {
    height: 76px;
    flex-shrink: 0;
}

/* Main two-column area fills the remaining screen */
.app-shell,
.layout,
.main-layout {
    height: calc(100vh - 76px);
    overflow: hidden;
}

/* Left chatbot column */
.left-panel,
.chat-panel,
.sidebar {
    height: calc(100vh - 76px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* This part scrolls, not the whole page */
.chat-scroll,
.chat-body,
.conversation {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding-bottom: 24px;
}

/* Input/search bar always stays at bottom */
.chat-input-area,
.input-area,
.message-form {
    flex-shrink: 0;
    position: sticky;
    bottom: 0;
    background: #f8fbff;
    padding: 16px 20px 20px;
    border-top: 1px solid #d9e8ff;
    z-index: 20;
}

/* --- Dashboard tabs --- */

.dashboard-tabs {
  margin-bottom: 16px;
}

.tab-input {
  display: none;
}

.tab-labels {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 8px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.tab-labels label {
  flex: 1;
  text-align: center;
  padding: 11px 14px;
  border-radius: 13px;
  font-weight: 800;
  color: var(--muted);
  cursor: pointer;
  font-size: 13px;
}

.tab-labels label:hover {
  background: var(--soft);
  color: var(--text);
}

.tab-panel {
  display: none;
}

#tab-overview:checked ~ .tab-labels label[for="tab-overview"],
#tab-market:checked ~ .tab-labels label[for="tab-market"],
#tab-advisor:checked ~ .tab-labels label[for="tab-advisor"],
#tab-competitors:checked ~ .tab-labels label[for="tab-competitors"] {
  background: var(--accent);
  color: white;
}

#tab-overview:checked ~ .tab-panels #panel-overview,
#tab-market:checked ~ .tab-panels #panel-market,
#tab-advisor:checked ~ .tab-panels #panel-advisor,
#tab-competitors:checked ~ .tab-panels #panel-competitors {
  display: block;
}

.empty-advisor-plan {
  background: #f8fafc;
  border: 1px dashed var(--border);
  border-radius: 18px;
  padding: 18px;
}

/* --- Fixed two-column app layout --- */

.app-shell {
  display: grid;
  grid-template-columns: 42% 58%;
  height: calc(100vh - 76px);
  overflow: hidden;
}

.left-panel {
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 76px);
  min-height: 0;
  overflow: hidden;
  background: #f8fbff;
}

.chat-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 24px 24px 18px;
}

.chat-input-area {
  flex-shrink: 0;
  background: white;
  padding: 16px 18px 18px;
  border-top: 1px solid var(--border);
  z-index: 20;
}

.input-row {
  display: flex;
  gap: 10px;
}

.chat-input {
  flex: 1;
}

.send-button {
  flex-shrink: 0;
}

.input-hint {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 11px;
}

.right-panel {
  height: calc(100vh - 76px);
  min-height: 0;
  overflow-y: auto;
  padding: 24px;
}

/* --- Revenue chart containment --- */

.revenue-chart {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 16px 0 8px;
}

.revenue-bars {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 150px;
  width: 100%;
  max-width: 100%;
}

.revenue-bar-wrap {
  flex: 1 1 0;
  min-width: 42px;
  text-align: center;
  color: var(--muted);
  font-size: 11px;
}

.revenue-bar {
  width: 100%;
  background: #bae6fd;
  border-radius: 10px 10px 0 0;
}

.revenue-bar.best {
  background: var(--accent);
}

.revenue-label {
  display: block;
  margin-top: 8px;
  white-space: nowrap;
}

.chart-note {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.revenue-bar.best {
  background: var(--accent);
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.18);
}

.revenue-bar-wrap.best-label .revenue-label {
  font-weight: 800;
  color: var(--accent-dark);
}

/* --- Better formatting for structured explanations --- */

.bubble p,
.explanation-content p {
  margin: 0 0 12px;
}

.bubble p:last-child,
.explanation-content p:last-child {
  margin-bottom: 0;
}

.bubble ul,
.explanation-content ul {
  margin: 8px 0 12px 20px;
  padding: 0;
}

.bubble li,
.explanation-content li {
  margin-bottom: 6px;
}

.bubble strong,
.explanation-content strong {
  font-weight: 850;
}

.explanation-card {
  padding: 22px;
}

.explanation-content {
  font-size: 15px;
  line-height: 1.55;
}

.guardrail-box {
  margin-top: 16px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 16px;
}

.guardrail-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 6px;
}

.guardrail-text {
  font-size: 14px;
  line-height: 1.45;
}

/* --- Competitor snapshot formatting --- */

.competitor-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.competitor-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 110px 90px;
  gap: 14px;
  align-items: center;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 16px;
}

.competitor-main {
  min-width: 0;
}

.competitor-name {
  font-weight: 850;
  font-size: 14px;
  line-height: 1.35;
  color: var(--text);
}

.competitor-source {
  color: var(--muted);
  font-size: 12px;
  margin-top: 4px;
}

.competitor-stat {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  text-align: center;
}

.competitor-label {
  color: var(--muted);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 4px;
}

.competitor-value {
  font-size: 14px;
  font-weight: 850;
  color: var(--text);
}

/* --- Compact quick actions above input --- */

.quick-actions-sticky {
  border-top: 1px solid var(--border);
  padding: 8px 0 10px;
  margin-bottom: 8px;
}

.quick-actions-title {
  font-size: 11px;
  font-weight: 850;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 6px;
}

.quick-actions-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0 2px 4px 0;
  scrollbar-width: thin;
}

.quick-actions-row form {
  margin: 0;
  flex: 0 0 auto;
}

.quick-action-chip {
  border: 1px solid var(--border);
  background: white;
  color: var(--text);
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 750;
  cursor: pointer;
  white-space: nowrap;
  max-width: none;
  overflow: visible;
  text-overflow: clip;
}

.quick-action-chip:hover {
  background: #f8fbff;
  border-color: #b9d8ff;
}

/* --- Advisor plan emphasis --- */

.advisor-panel {
  border: 1px solid var(--border);
  border-radius: 24px;
  background: white;
  padding: 22px;
}

.advisor-empty-state {
  border: 1px dashed #b9d8ff;
  background: linear-gradient(180deg, #fbfdff 0%, #f7fbff 100%);
  border-radius: 20px;
  padding: 28px 24px;
}

.advisor-empty-icon {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #eaf4ff;
  color: var(--accent);
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 14px;
}

.advisor-empty-title {
  font-size: 26px;
  font-weight: 850;
  color: var(--text);
  margin-bottom: 8px;
}

.advisor-empty-text {
  font-size: 15px;
  line-height: 1.55;
  color: var(--muted);
  max-width: 760px;
}

.advisor-empty-note {
  margin-top: 16px;
  font-size: 14px;
  color: var(--text);
  background: white;
  border: 1px solid var(--border);
  display: inline-block;
  padding: 10px 14px;
  border-radius: 999px;
}

/* --- Left panel cleanup --- */

.left-panel {
  background: #f8fbff;
}

.chat-scroll {
  padding: 18px 20px 12px;
}

.advisor-mode-card,
.strategy-summary-card {
  padding: 18px 18px 16px;
  border-radius: 22px;
}

.msg-row {
  margin-bottom: 14px;
}

.bubble {
  max-width: 88%;
  border-radius: 22px;
  padding: 16px 18px;
  line-height: 1.5;
}

.msg-row.user .bubble {
  margin-left: auto;
}

.chat-input-area {
  background: white;
  padding: 8px 14px 10px;
  border-top: 1px solid var(--border);
  box-shadow: 0 -6px 20px rgba(15, 23, 42, 0.04);
}

.card h3,
.card h2,
.tab-panel h2 {
  margin-top: 0;
  margin-bottom: 14px;
}

.card {
  border-radius: 24px;
  padding: 22px;
}

.tabs {
  position: sticky;
  top: 16px;
  z-index: 10;
  background: #f8fbff;
  padding-bottom: 8px;
}

</style>
"""


PHASES = ["product", "audience", "positioning", "differentiation", "objective", "constraints"]

PHASE_LABELS = {
    "product": "Product",
    "audience": "Customer",
    "positioning": "Positioning",
    "differentiation": "Edge",
    "objective": "Goal",
    "constraints": "Constraints",
    "confirm": "Confirm",
    "complete": "Complete",
}

OBJECTIVE_LABELS = {
    "maximize_growth": "Maximize growth",
    "maximize_revenue": "Maximize revenue",
    "competitive_entry": "Competitive entry",
    "premium_positioning": "Premium positioning",
}


def money(value):
    return f"${float(value):,.0f}"


def price(value):
    return f"${float(value):,.2f}"


def percent(value):
    return f"{float(value):.2%}"


def safe_text(value):
    return html.escape(str(value or ""), quote=True)


def encode_json(value):
    return html.escape(json.dumps(value), quote=True)


def decode_json(value, default):
    try:
        return json.loads(value) if value else default
    except Exception:
        return default


def blank_profile():
    return {
        "product_query": None,
        "business_type": None,
        "audience": None,
        "positioning": None,
        "key_features": [],
        "differentiation": None,
        "objective": None,
        "cost_floor": None,
        "sales_channel": "online store",
        "launch_stage": "new_launch",
        "competitor_frame": None,
        "price_sensitivity": None,
        "risk_tolerance": "medium",
        "constraints_answered": False,
    }


def has_value(value):
    if value is None:
        return False
    if isinstance(value, list):
        return len([x for x in value if str(x).strip()]) > 0
    return str(value).strip() != "" and str(value).lower() != "none"


def clean_value(value, fallback="Not specified"):
    if not has_value(value):
        return fallback
    if isinstance(value, list):
        return ", ".join(str(x) for x in value if str(x).strip())
    return str(value)


def objective_label(value):
    if not value:
        return "Not specified"
    return OBJECTIVE_LABELS.get(value, str(value).replace("_", " ").title())


def extract_cost_floor(text):
    text = text or ""
    lower = text.lower()

    if "no" in lower and ("constraint" in lower or "floor" in lower or "minimum" in lower):
        return None

    constraint_words = ["cost", "cogs", "floor", "minimum", "min", "less than", "below", "at least", "margin"]
    if not any(word in lower for word in constraint_words):
        return None

    matches = re.findall(r"\$?\s*(\d+(?:\.\d+)?)", text)
    if not matches:
        return None

    return max(float(x) for x in matches)


def objective_from_text(text):
    lower = text.lower()

    if any(x in lower for x in ["grow", "growth", "adoption", "customers", "volume"]):
        return "maximize_growth"
    if any(x in lower for x in ["premium", "luxury", "high-end", "signal quality"]):
        return "premium_positioning"
    if any(x in lower for x in ["competitive", "entry", "market share", "undercut"]):
        return "competitive_entry"
    if any(x in lower for x in ["revenue", "profit", "margin"]):
        return "maximize_revenue"

    return None


def positioning_from_text(text):
    lower = text.lower()

    if any(x in lower for x in ["budget", "cheap", "affordable", "entry", "cheapest"]):
        return "budget"
    if any(x in lower for x in ["premium", "luxury", "high-end", "specialist", "flagship"]):
        return "premium"
    if any(x in lower for x in ["value", "mid", "balanced", "mainstream", "accessible"]):
        return "mid-market"

    return None


def seed_profile_from_text(profile, text):
    try:
        parsed = parse_pricing_prompt(text)
    except Exception:
        parsed = {}

    if parsed.get("product_query"):
        profile["product_query"] = parsed.get("product_query")

    if parsed.get("business_type"):
        profile["business_type"] = parsed.get("business_type")

    if parsed.get("audience"):
        profile["audience"] = parsed.get("audience")

    if parsed.get("positioning"):
        profile["positioning"] = parsed.get("positioning")

    if parsed.get("key_features"):
        profile["key_features"] = parsed.get("key_features")

    if parsed.get("differentiation"):
        profile["differentiation"] = parsed.get("differentiation")

    objective = objective_from_text(text)
    if objective:
        profile["objective"] = objective

    cost_floor = extract_cost_floor(text)
    if cost_floor:
        profile["cost_floor"] = cost_floor
        profile["constraints_answered"] = True

    return profile


def apply_message_to_profile(profile, phase, message):
    message = message.strip()

    if phase == "product":
        profile = seed_profile_from_text(profile, message)
        if not profile.get("product_query"):
            profile["product_query"] = message

    elif phase == "audience":
        profile["audience"] = message

        lower = message.lower()
        if "beginner" in lower or "budget" in lower:
            profile["price_sensitivity"] = "high"
        elif "professional" in lower or "power" in lower:
            profile["price_sensitivity"] = "medium"
        elif "enthusiast" in lower or "quality" in lower:
            profile["price_sensitivity"] = "medium"

    elif phase == "positioning":
        profile["positioning"] = positioning_from_text(message) or message

    elif phase == "differentiation":
        profile["differentiation"] = message
        profile["key_features"] = [x.strip() for x in re.split(r",| and ", message) if x.strip()]

    elif phase == "objective":
        profile["objective"] = objective_from_text(message) or "maximize_revenue"

    elif phase == "constraints":
        cost_floor = extract_cost_floor(message)
        if cost_floor:
            profile["cost_floor"] = cost_floor
        profile["constraints_answered"] = True

    return profile


def next_phase(profile):
    if not has_value(profile.get("product_query")):
        return "product"
    if not has_value(profile.get("audience")):
        return "audience"
    if not has_value(profile.get("positioning")):
        return "positioning"
    if not has_value(profile.get("differentiation")) and not has_value(profile.get("key_features")):
        return "differentiation"
    if not has_value(profile.get("objective")):
        return "objective"
    if not profile.get("constraints_answered"):
        return "constraints"
    return "confirm"


def phase_question(phase, profile):
    product = clean_value(profile.get("product_query"), "this product")
    audience = clean_value(profile.get("audience"), "your target customer")

    if phase == "product":
        return "Great, I’ll help build a launch pricing strategy. What product are we pricing?"
    if phase == "audience":
        return f"Got it, we are pricing **{product}**. Who are you trying to win first?"
    if phase == "positioning":
        return f"Perfect. For **{audience}**, how should this product be positioned in the market?"
    if phase == "differentiation":
        return f"Why would **{audience}** choose your **{product}** over the alternatives?"
    if phase == "objective":
        return "What is the main pricing goal for this launch?"
    if phase == "constraints":
        return "Any cost floor, minimum acceptable price, or margin constraint I should respect?"
    if phase == "confirm":
        return "Here is the strategy profile I’ll use. Does this look right before I build the pricing strategy?"
    return "What should we adjust?"



def phase_chips(phase):
    if phase == "product":
        return [
            "DJ turntables",
            "Wireless headphones",
            "Standing desk",
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
            "Cheapest credible option",
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

    if phase == "constraints":
        return [
            "No hard constraint",
            "Cost floor is $50",
            "Cost floor is $100",
            "Cost floor is $150",
        ]

    if phase == "confirm":
        return [
            "Looks right, build strategy",
            "Edit customer",
            "Edit positioning",
            "Edit goal",
            "Add price constraint",
        ]

    if phase == "complete":
        return [
            "Build bundle strategy",
            "Create 30-day test plan",
            "Pressure-test biggest risks",
            "Run growth scenario",
            "Run premium scenario",
            "Add a $100 cost floor",
        ]

    return []

def post_analysis_questions(result):
    fallback_questions = [
        "Why is this the right launch price?",
        "Are we priced too low compared to the market?",
        "What are the biggest risks?",
        "Build a 30-day launch test plan",
        "Build a bundle strategy",
    ]

    questions = fallback_questions

    if result:
        try:
            questions = generate_followup_questions_after_analysis(
                strategy_profile=result.get("strategy_profile", {}),
                market_summary=result.get("market_summary", {}),
                recommendation=result.get("recommendation", {}),
                max_questions=5,
            )
        except Exception:
            questions = fallback_questions

    required_questions = [
        "How does this compare to the market?",
        "Build a 30-day launch test plan",
    ]

    final_questions = []

    for q in required_questions + questions:
        q = str(q).strip()
        if not q:
            continue

        lower = q.lower()

        # Remove vague test question because the 30-day plan is clearer.
        if "what should we test first" in lower:
            continue

        # Avoid duplicate 30-day/test-plan wording.
        already_has_30_day = any(
            "30-day" in existing.lower() or "30 day" in existing.lower()
            for existing in final_questions
        )

        if already_has_30_day and (
            "30-day" in lower
            or "30 day" in lower
            or "test plan" in lower
        ):
            continue

        if q not in final_questions:
            final_questions.append(q)

    return final_questions[:6]

def is_strategy_update_request(message):
    lower = message.lower().strip()

    update_markers = [
        "what if",
        "i want",
        "switch",
        "change",
        "update",
        "rerun",
        "run",
        "scenario",
        "target",
        "instead",
    ]

    strategy_terms = [
        "premium",
        "budget",
        "affordable",
        "growth",
        "grow",
        "revenue",
        "competitive",
        "cost floor",
        "constraint",
        "margin",
    ]

    return any(marker in lower for marker in update_markers) and any(
        term in lower for term in strategy_terms
    )
    
def is_advisor_question(message):
    lower = message.lower().strip()

    question_starters = [
        "why",
        "what",
        "how",
        "are",
        "can",
        "should",
        "which",
    ]

    starts_like_question = any(lower.startswith(word + " ") for word in question_starters)

    return lower.endswith("?") or starts_like_question

def render_post_analysis_questions(result, profile, phase, history, session_id):
    questions = post_analysis_questions(result)

    profile_value = encode_json(profile)
    history_value = encode_json(history)

    question_html = '<div class="action-group-title">Questions you might ask next</div>'

    for question in questions:
        button_class = "chip action-chip"

        question_html += f"""
        <form method="post" action="/chat">
          <input type="hidden" name="message" value="{safe_text(question)}">
          <input type="hidden" name="profile" value="{profile_value}">
          <input type="hidden" name="phase" value="{safe_text(phase)}">
          <input type="hidden" name="history" value="{history_value}">
          <input type="hidden" name="session_id" value="{safe_text(session_id)}">
          <button class="{button_class}" type="submit">{safe_text(question)}</button>
        </form>
        """

    return f'<div class="chips advisor-actions">{question_html}</div>'

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

def profile_to_context(profile):
    objective = objective_label(profile.get("objective"))
    cost_floor = profile.get("cost_floor")

    lines = [
        f"Product: {clean_value(profile.get('product_query'))}",
        f"Business type: {clean_value(profile.get('business_type'))}",
        f"Target customer: {clean_value(profile.get('audience'))}",
        f"Positioning: {clean_value(profile.get('positioning'))}",
        f"Differentiation: {clean_value(profile.get('differentiation'))}",
        f"Key features: {clean_value(profile.get('key_features'))}",
        f"Pricing objective: {objective}",
        f"Sales channel: {clean_value(profile.get('sales_channel'))}",
        f"Launch stage: {clean_value(profile.get('launch_stage'))}",
    ]

    if cost_floor:
        lines.append(f"Minimum acceptable price / cost floor: ${cost_floor:.2f}")

    return "\n".join(lines)


def format_explanation_markdown(text):
    if not text:
        return ""

    raw = str(text).strip().replace("\r\n", "\n")

    # Normalize section labels.
    for label in ["Direct answer", "Why", "Tradeoff", "Next step", "Guardrail"]:
        raw = raw.replace(f"**{label}:**", f"{label}:")
        raw = raw.replace(f"*{label}:*", f"{label}:")
        raw = raw.replace(f"{label}: ", f"{label}: ")

    # Force major labels onto their own lines even if the LLM puts them inline.
    for label in ["Direct answer", "Why", "Tradeoff", "Next step", "Guardrail"]:
        raw = re.sub(
            rf"\s*{label}:\s*",
            f"\n\n{label}: ",
            raw,
            flags=re.IGNORECASE,
        )

    # Remove guardrail from the explanation because it is rendered separately.
    raw = re.sub(
        r"\n\nGuardrail:\s*.*$",
        "",
        raw,
        flags=re.IGNORECASE | re.DOTALL,
    )

    labels = ["Direct answer", "Why", "Tradeoff", "Next step"]
    sections = {label: "" for label in labels}
    current = None

    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue

        matched_label = None
        for label in labels:
            prefix = f"{label}:"
            if line.lower().startswith(prefix.lower()):
                matched_label = label
                current = label
                sections[label] += line[len(prefix):].strip()
                break

        if matched_label:
            continue

        if current:
            if line.startswith("-") or line.startswith("•"):
                sections[current] += "\n" + line
            else:
                sections[current] += " " + line

    direct = sections["Direct answer"].strip()
    why = sections["Why"].strip()
    tradeoff = sections["Tradeoff"].strip()
    next_step = sections["Next step"].strip()

    parts = []

    if direct:
        parts.append(f"**Direct answer:** {direct}")

    if why:
        why = why.replace("•", "-")
        why_lines = [line.strip() for line in why.split("\n") if line.strip()]
        bullets = []

        for line in why_lines:
            line = line.lstrip("-").strip()
            if line:
                bullets.append(line)

        if bullets:
            bullet_text = "\n".join(f"- {item}" for item in bullets[:2])
            parts.append(f"**Why:**\n\n{bullet_text}")
        else:
            parts.append(f"**Why:** {why}")

    if tradeoff:
        parts.append(f"**Tradeoff:** {tradeoff}")

    if next_step:
        parts.append(f"**Next step:** {next_step}")

    return "\n\n".join(parts)

def render_topbar():
    return """
    <div class="topbar">
      <div class="logo">↗</div>
      <div>
        <h1>Pricing Strategy Agent</h1>
        <p>AI launch pricing strategist</p>
      </div>
    </div>
    """


def render_history(history):
    html_parts = ""

    for item in history:
        role = item.get("role", "agent")
        content = item.get("content", "")

        if role == "user":
            html_parts += f"""
            <div class="msg-row user">
              <div class="bubble">{safe_text(content)}</div>
            </div>
            """
        else:
            rendered_content = content.strip()

            if any(label in rendered_content for label in ["Direct answer:", "Why:", "Tradeoff:", "Next step:"]):
                rendered_content = format_explanation_markdown(rendered_content)

            html_parts += f"""
            <div class="msg-row agent">
              <div class="agent-icon">✦</div>
              <div class="bubble">{markdown.markdown(rendered_content, extensions=["extra"])}</div>
            </div>
            """
    return html_parts

def compact_advisor_history(history):
    """
    After the strategy is built, hide the setup transcript and only show
    the most relevant advisor-mode messages.
    """
    if not history:
        return []

    build_index = None

    for i, item in enumerate(history):
        content = item.get("content", "")
        role = item.get("role", "")

        if role == "agent" and (
            "I built the launch pricing strategy" in content
            or "Updated recommendation" in content
            or "I updated the strategy" in content
        ):
            build_index = i

    if build_index is None:
        return history[-4:]

    advisor_history = history[build_index:]

    if len(advisor_history) <= 5:
        return advisor_history

    # Keep the original build summary plus the latest advisor exchange.
    return [advisor_history[0]] + advisor_history[-4:]


def completed_count(profile):
    count = 0
    count += 1 if has_value(profile.get("product_query")) else 0
    count += 1 if has_value(profile.get("audience")) else 0
    count += 1 if has_value(profile.get("positioning")) else 0
    count += 1 if has_value(profile.get("differentiation")) or has_value(profile.get("key_features")) else 0
    count += 1 if has_value(profile.get("objective")) else 0
    count += 1 if profile.get("constraints_answered") else 0
    return count



def render_setup_progress(profile, phase):
    if phase == "complete":
        product = clean_value(profile.get("product_query"), "Product")
        customer = clean_value(profile.get("audience"), "Customer")
        goal = objective_label(profile.get("objective"))

        return f"""
        <div class="setup-card">
          <div class="advisor-label">Advisor Mode</div>
          <div class="setup-title">Strategy built ✓</div>
          <p class="small" style="margin:0;">
            {safe_text(product)} · {safe_text(customer)} · {safe_text(goal)}
          </p>
          <p class="small" style="margin:8px 0 0;">
            Use the actions below to pressure-test, revise, or extend the launch pricing strategy.
          </p>
        </div>
        """

    done = completed_count(profile)
    width = int((done / len(PHASES)) * 100)

    steps = ""
    for p in PHASES:
        complete = False

        if p == "product":
            complete = has_value(profile.get("product_query"))
        elif p == "audience":
            complete = has_value(profile.get("audience"))
        elif p == "positioning":
            complete = has_value(profile.get("positioning"))
        elif p == "differentiation":
            complete = has_value(profile.get("differentiation")) or has_value(profile.get("key_features"))
        elif p == "objective":
            complete = has_value(profile.get("objective"))
        elif p == "constraints":
            complete = profile.get("constraints_answered")

        cls = "step done" if complete else "step"
        steps += f'<div class="{cls}">{"✓" if complete else "○"} {PHASE_LABELS[p]}</div>'

    return f"""
    <div class="setup-card">
      <div class="setup-title">Strategy setup: {done} of {len(PHASES)} complete</div>
      <div class="progress-track"><div class="progress-fill" style="width:{width}%"></div></div>
      <div class="progress-steps">{steps}</div>
    </div>
    """


def render_chip_forms(chips, profile, phase, history, session_id):
    if not chips:
        return ""

    profile_value = encode_json(profile)
    history_value = encode_json(history)

    if phase == "complete":
        advice_actions = [
            "Build bundle strategy",
            "Create 30-day test plan",
            "Pressure-test biggest risks",
        ]

        strategy_actions = [
            "Run growth scenario",
            "Run premium scenario",
            "Add a $100 cost floor",
        ]

        chip_html = '<div class="action-group-title">Get advice</div>'

        for chip in advice_actions:
            chip_html += f"""
            <form method="post" action="/chat">
              <input type="hidden" name="message" value="{safe_text(chip)}">
              <input type="hidden" name="profile" value="{profile_value}">
              <input type="hidden" name="phase" value="{safe_text(phase)}">
              <input type="hidden" name="history" value="{history_value}">
              <input type="hidden" name="session_id" value="{safe_text(session_id)}">
              <button class="chip action-chip" type="submit">{safe_text(chip)}</button>
            </form>
            """

        chip_html += '<div class="action-group-title">Update strategy</div>'

        for chip in strategy_actions:
            chip_html += f"""
            <form method="post" action="/chat">
              <input type="hidden" name="message" value="{safe_text(chip)}">
              <input type="hidden" name="profile" value="{profile_value}">
              <input type="hidden" name="phase" value="{safe_text(phase)}">
              <input type="hidden" name="history" value="{history_value}">
              <input type="hidden" name="session_id" value="{safe_text(session_id)}">
              <button class="chip action-chip primary-chip" type="submit">{safe_text(chip)}</button>
            </form>
            """

        return f'<div class="chips advisor-actions">{chip_html}</div>'

    chip_html = ""
    for chip in chips:
        primary = "primary-chip" if "build" in chip.lower() or "looks right" in chip.lower() else ""
        chip_html += f"""
        <form method="post" action="/chat">
          <input type="hidden" name="message" value="{safe_text(chip)}">
          <input type="hidden" name="profile" value="{profile_value}">
          <input type="hidden" name="phase" value="{safe_text(phase)}">
          <input type="hidden" name="history" value="{history_value}">
          <input type="hidden" name="session_id" value="{safe_text(session_id)}">
          <button class="chip {primary}" type="submit">{safe_text(chip)}</button>
        </form>
        """

    return f'<div class="chips">{chip_html}</div>'


def canvas_row(label, value):
    value_html = safe_text(clean_value(value))
    cls = "" if has_value(value) else "empty-value"

    return f"""
    <div class="canvas-row">
      <div class="canvas-label">{safe_text(label)}</div>
      <div class="canvas-value {cls}">{value_html}</div>
    </div>
    """


def render_strategy_canvas(profile):
    cost_floor = profile.get("cost_floor")
    cost_text = f"${cost_floor:.2f}" if cost_floor else ("No hard constraint" if profile.get("constraints_answered") else None)

    return f"""
    <div class="card">
      <h2>Strategy Canvas</h2>
      <p class="small">This fills in as the chat learns the product strategy.</p>

      {canvas_row("Product", profile.get("product_query"))}
      {canvas_row("Customer", profile.get("audience"))}
      {canvas_row("Positioning", profile.get("positioning"))}
      {canvas_row("Differentiation", profile.get("differentiation"))}
      {canvas_row("Pricing goal", objective_label(profile.get("objective")) if profile.get("objective") else None)}
      {canvas_row("Cost / price floor", cost_text)}
      {canvas_row("Sales channel", profile.get("sales_channel"))}
      {canvas_row("Launch stage", profile.get("launch_stage"))}
    </div>

    <div class="card">
      <h3>How this will work</h3>
      <div class="grid-2">
        <div class="metric">
          <div class="metric-label">1. Discover</div>
          <p>Build the product, customer, positioning, and goal profile.</p>
        </div>
        <div class="metric">
          <div class="metric-label">2. Confirm</div>
          <p>Review the strategy assumptions before running the pricing model.</p>
        </div>
        <div class="metric">
          <div class="metric-label">3. Simulate</div>
          <p>Use live market data and guardrails to recommend a launch price.</p>
        </div>
        <div class="metric">
          <div class="metric-label">4. Iterate</div>
          <p>Ask what-if questions to adjust growth, premium, or constraint scenarios.</p>
        </div>
      </div>
    </div>
    """

def make_revenue_chart(sim, recommended_price):
    full_df = sim.sort_values("price").copy().reset_index(drop=True)

    target_bars = 12
    closest_idx = int((full_df["price"] - recommended_price).abs().idxmin())
    highlight_price = float(full_df.loc[closest_idx, "price"])

    if len(full_df) > target_bars:
        base_count = target_bars - 1
        base_indices = [
            round(i * (len(full_df) - 1) / (base_count - 1))
            for i in range(base_count)
        ]
        selected_indices = sorted(set(base_indices + [closest_idx]))
        chart_df = full_df.iloc[selected_indices].copy()
    else:
        chart_df = full_df.copy()

    max_revenue = chart_df["expected_revenue"].max()
    bars = ""

    for _, row in chart_df.iterrows():
        height = max(8, (row["expected_revenue"] / max_revenue) * 120)
        is_best = abs(float(row["price"]) - highlight_price) < 0.001
        best_class = "best" if is_best else ""
        wrap_class = "best-label" if is_best else ""

        bars += f"""
        <div class="revenue-bar-wrap {wrap_class}">
            <div
                class="revenue-bar {best_class}"
                style="height: {height}px;"
                title="{price(row['price'])}: {money(row['expected_revenue'])}"
            ></div>
            <span class="revenue-label">{price(row["price"])}</span>
        </div>
        """

    return f"""
    <div class="revenue-chart">
        <div class="revenue-bars">
            {bars}
        </div>
    </div>
    <p class="chart-note">Recommended price is highlighted.</p>
    """


def make_products_table(products_df):
    if products_df is None or products_df.empty:
        return "<p>No product details available.</p>"

    name_col = None
    for col in ["product_name", "name", "title"]:
        if col in products_df.columns:
            name_col = col
            break

    if not name_col or "price" not in products_df.columns:
        return "<p>No product details available.</p>"

    display = products_df.head(6).copy()

    rows_html = ""

    for _, row in display.iterrows():
        product_name = clean_value(row.get(name_col), "Unknown product")
        product_price = price(row.get("price", 0))

        rating = row.get("rating", None)
        rating_text = f"{float(rating):.1f} ★" if has_value(rating) else "N/A"

        source = clean_value(row.get("source"), "Unknown source")

        rows_html += f"""
        <div class="competitor-row">
          <div class="competitor-main">
            <div class="competitor-name">{safe_text(product_name)}</div>
            <div class="competitor-source">{safe_text(source)}</div>
          </div>

          <div class="competitor-stat">
            <div class="competitor-label">Price</div>
            <div class="competitor-value">{product_price}</div>
          </div>

          <div class="competitor-stat">
            <div class="competitor-label">Rating</div>
            <div class="competitor-value">{safe_text(rating_text)}</div>
          </div>
        </div>
        """

    return f"""
    <div class="competitor-list">
      {rows_html}
    </div>
    """


def advisor_plan_from_message(message, result):
    lower = message.lower()
    profile = result.get("strategy_profile", {})
    rec = result["recommendation"]

    product = clean_value(profile.get("product_query") or result.get("product_query"), "the product")
    customer = clean_value(profile.get("audience"), "the target customer")
    base_price = float(rec["recommended_price"])
    cost_floor = float(profile.get("cost_floor") or 0)

    if "bundle" in lower:
        base_price = max(base_price, cost_floor)
        return {
            "title": "Bundle Strategy",
            "summary": f"Use bundles to lift average order value while keeping the base {product} price visible.",
            "boxes": [
                {
                    "title": "Base Product",
                    "value": price(base_price),
                    "detail": "Keeps the entry offer simple and easy to compare.",
                },
                {
                    "title": "Starter Bundle",
                    "value": price(base_price * 1.15),
                    "detail": f"Best default upsell for {customer}.",
                },
                {
                    "title": "Premium Bundle",
                    "value": price(base_price * 1.30),
                    "detail": "Captures customers with higher willingness to pay.",
                },
            ],
            "next_step": "Test base product vs starter bundle and compare conversion, revenue per visitor, and average order value.",
        }

    if "30 days" in lower or "test" in lower or "experiment" in lower:
        effective_base_price = max(base_price, cost_floor)
        low_price = max(effective_base_price * 0.92, cost_floor)
        base_price = effective_base_price
        high_price = effective_base_price * 1.08

        return {
            "title": "30-Day Test Plan",
            "summary": "Treat the recommendation as a launch hypothesis, then validate it with price, messaging, and bundle tests.",
            "boxes": [
                {
                    "title": "Price Test",
                    "value": f"{price(low_price)} / {price(base_price)} / {price(high_price)}",
                    "detail": "Compare revenue per visitor, not only conversion.",
                },
                {
                    "title": "Messaging Test",
                    "value": "Value vs Specialist",
                    "detail": "Test whether customers respond more to savings or expertise.",
                },
                {
                    "title": "Bundle Test",
                    "value": price(base_price * 1.15),
                    "detail": "Measure bundle attach rate and average order value.",
                },
            ],
            "next_step": "Keep the version that improves revenue per visitor without hurting perceived quality.",
        }

    if "risk" in lower:
        return {
            "title": "Risk Review",
            "summary": "The biggest risk is not only price. It is whether customers understand why this product deserves its price.",
            "boxes": [
                {
                    "title": "Market Risk",
                    "value": "Comparable quality",
                    "detail": "Competitor data may include products that are not true substitutes.",
                },
                {
                    "title": "Positioning Risk",
                    "value": "Value proof",
                    "detail": "Premium or specialist positioning needs clear evidence.",
                },
                {
                    "title": "Demand Risk",
                    "value": "Conversion tradeoff",
                    "detail": "Higher price may lift revenue per order but reduce early adoption.",
                },
            ],
            "next_step": "If conversion is weak but engagement is strong, improve messaging before cutting price.",
        }

    return None


def render_active_advisor_plan(result):
    plan = result.get("advisor_plan")

    if not plan:
        return ""

    boxes_html = ""
    for box in plan.get("boxes", []):
        boxes_html += f"""
        <div class="plan-box">
        <div class="plan-box-title">{safe_text(box.get("title"))}</div>
        <div class="metric-value" style="font-size:18px;">{safe_text(box.get("value"))}</div>
        <p class="small">{safe_text(box.get("detail"))}</p>
        </div>
        """

    return f"""
    <div class="card active-plan-card">
    <h3>Active Advisor Plan: {safe_text(plan.get("title"))}</h3>
    <p>{safe_text(plan.get("summary"))}</p>
    <div class="plan-grid">
        {boxes_html}
    </div>
    <p class="small" style="margin-top:12px;"><strong>Next step:</strong> {safe_text(plan.get("next_step"))}</p>
    </div>
    """

def render_dashboard(result):
    rec = result["recommendation"]
    summary = result["market_summary"]
    sim = result["simulation"].copy()
    products = result["products"].copy()
    profile = result.get("strategy_profile", {})
    explanation = result.get("explanation", "")
    formatted_explanation = format_explanation_markdown(explanation)
    
    cost_floor_text = (
        f"${profile.get('cost_floor'):.2f}"
        if profile.get("cost_floor")
        else "No hard constraint"
    )

    guardrail_html = ""
    if rec.get("guardrail_note"):
        guardrail_html = f"""
        <div class="metric">
          <div class="metric-label">Guardrail Applied</div>
          <p>{safe_text(rec["guardrail_note"])}</p>
        </div>
        """
    
    active_tab = result.get("active_tab", "overview")

    overview_checked = "checked" if active_tab == "overview" else ""
    market_checked = "checked" if active_tab == "market" else ""
    advisor_checked = "checked" if active_tab == "advisor" else ""
    competitors_checked = "checked" if active_tab == "competitors" else ""

    advisor_plan_html = render_active_advisor_plan(result)

    if not advisor_plan_html:
        advisor_plan_html = """
        <div class="card advisor-panel">
          <div class="advisor-empty-state">
            <div class="advisor-empty-icon">✦</div>
            <div class="advisor-empty-title">Generate an advisor plan</div>
            <div class="advisor-empty-text">
              Use one of the quick actions on the left to generate a 30-day launch test plan,
              bundle strategy, or risk review.
            </div>
            <div class="advisor-empty-note">
              Best next step: <strong>Build a 30-day launch test plan</strong>
            </div>
          </div>
        </div>
        """

    return f"""
    <div class="dashboard-tabs">
      <input class="tab-input" type="radio" name="dashboard-tab" id="tab-overview" {overview_checked}>
      <input class="tab-input" type="radio" name="dashboard-tab" id="tab-market" {market_checked}>
      <input class="tab-input" type="radio" name="dashboard-tab" id="tab-advisor" {advisor_checked}>
      <input class="tab-input" type="radio" name="dashboard-tab" id="tab-competitors" {competitors_checked}>

      <div class="tab-labels">
        <label for="tab-overview">Overview</label>
        <label for="tab-market">Market</label>
        <label for="tab-advisor">Advisor Plan</label>
        <label for="tab-competitors">Competitors</label>
      </div>

      <div class="tab-panels">

        <div class="tab-panel" id="panel-overview">
          <div class="card">
            <h2>Launch Pricing Strategy</h2>
            <p class="small">Built from the confirmed strategy profile.</p>

            <div class="grid">
              <div class="metric">
                <div class="metric-label">Recommended Launch Price</div>
                <div class="metric-value">{price(rec["recommended_price"])}</div>
                <p class="small">Market position: {safe_text(rec["market_position"])}</p>
              </div>

              <div class="metric">
                <div class="metric-label">Expected Revenue</div>
                <div class="metric-value">{money(rec["expected_revenue"])}</div>
                <p class="small">Per month</p>
              </div>

              <div class="metric">
                <div class="metric-label">Demand Estimate</div>
                <div class="metric-value">{percent(rec["conversion_rate"])}</div>
                <p class="small">{int(rec["expected_customers"])} customers / month</p>
              </div>
            </div>
          </div>

          <div class="card">
            <h3>Confirmed Strategy Profile</h3>
            {canvas_row("Product", profile.get("product_query") or result.get("product_query"))}
            {canvas_row("Customer", profile.get("audience"))}
            {canvas_row("Positioning", profile.get("positioning"))}
            {canvas_row("Differentiation", profile.get("differentiation"))}
            {canvas_row("Goal", objective_label(profile.get("objective")))}
            {canvas_row("Cost floor", cost_floor_text)}
          </div>

          <div class="card explanation-card">
            <h3>Why this price works</h3>
            <div class="explanation-content">
              {markdown.markdown(formatted_explanation, extensions=["extra"])}
            </div>
            {guardrail_html}
          </div>
        </div>

        <div class="tab-panel" id="panel-market">
          <div class="card">
            <h2>Market Snapshot</h2>
            <p class="small">Use this to compare the recommendation against observed market pricing.</p>

            <div class="grid">
              <div class="metric">
                <div class="metric-label">Market Median</div>
                <div class="metric-value">{price(summary["median_price"])}</div>
              </div>
              <div class="metric">
                <div class="metric-label">Products Analyzed</div>
                <div class="metric-value">{int(summary["num_products"])}</div>
              </div>
              <div class="metric">
                <div class="metric-label">Price Range</div>
                <div class="metric-value">{price(summary["min_price"])}-{price(summary["max_price"])}</div>
              </div>
            </div>
          </div>

          <div class="card">
            <h3>Revenue Curve</h3>
            {make_revenue_chart(sim, rec["recommended_price"])}
          </div>
        </div>

        <div class="tab-panel" id="panel-advisor">
          {advisor_plan_html}
        </div>

        <div class="tab-panel" id="panel-competitors">
          <div class="card">
            <h2>Competitor Snapshot</h2>
            <p class="small">Representative products pulled from live shopping results.</p>
            {make_products_table(products)}
          </div>
        </div>

      </div>
    </div>
    """


def render_page(profile, phase, history, session_id="", result=None):
    profile_value = encode_json(profile)
    history_value = encode_json(history)

    chips = phase_chips(phase)

    if phase == "complete" and result:
        chips_html = render_post_analysis_questions(
            result, profile, phase, history, session_id
        )
    else:
        chips_html = render_chip_forms(
            chips, profile, phase, history, session_id
        )

    right_side = render_dashboard(result) if result else render_strategy_canvas(profile)
    quick_actions_html = render_quick_actions(result, profile, phase, history, session_id)

    if phase == "complete":
        visible_history = compact_advisor_history(history)

        archive_note = """
        <div class="chat-archive-note">
          Setup transcript is collapsed. Advisor Mode is focused on the current strategy.
        </div>
        """

        discussion_title = """
        <div class="recent-discussion-title">
          Recent advisor discussion
        </div>
        """

        chat_body = f"""
          {render_setup_progress(profile, phase)}
          {archive_note}
          <div class="advisor-spacer"></div>
          {discussion_title}
          {render_history(visible_history)}
        """
    else:
        chat_body = f"""
          {render_setup_progress(profile, phase)}
          {render_history(history)}
          {chips_html}
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PricePilot</title>
        {STYLE}
    </head>
    <body>
        {render_topbar()}

        <main class="app-shell">
            <section class="left-panel">
                <div class="chat-scroll">
                    {chat_body}
                </div>

                <div class="chat-input-area">
                  {quick_actions_html}

                  <form method="post" action="/chat">
                      <input type="hidden" name="profile" value="{profile_value}">
                      <input type="hidden" name="phase" value="{safe_text(phase)}">
                      <input type="hidden" name="history" value="{history_value}">
                      <input type="hidden" name="session_id" value="{safe_text(session_id)}">

                      <div class="input-row">
                          <input
                              class="chat-input"
                              type="text"
                              name="message"
                              placeholder="Ask a follow-up or update the strategy..."
                              autocomplete="off"
                              required
                          >
                          <button class="send-button" type="submit">Send</button>
                      </div>

                      <p class="input-hint">
                          PricePilot builds launch pricing strategies from product context, market data, and constraints.
                      </p>
                  </form>
              </div>
            </section>

            <section class="right-panel">
                {right_side}
            </section>
        </main>

        <script>
          window.addEventListener("load", function () {{
            const chatScroll = document.querySelector(".chat-scroll");
            if (chatScroll) {{
              chatScroll.scrollTop = chatScroll.scrollHeight;
            }}

            const input = document.querySelector(".chat-input");
            if (input) {{
              input.focus();
            }}
          }});
        </script>
    </body>
    </html>
    """


def ask_current_phase(profile, phase, history):
    history.append({"role": "agent", "content": phase_question(phase, profile)})
    return history


def run_strategy(profile):
    context = profile_to_context(profile)
    result = run_pricing_agent(context)

    if not result.get("error"):
        result["strategy_profile"] = profile

    return result


def edit_phase_from_message(message):
    lower = message.lower()

    if "customer" in lower:
        return "audience"
    if "position" in lower:
        return "positioning"
    if "goal" in lower:
        return "objective"
    if "constraint" in lower or "floor" in lower:
        return "constraints"

    return None


@app.get("/", response_class=HTMLResponse)
def home():
    profile = blank_profile()
    phase = "product"

    history = [
        {
            "role": "agent",
            "content": phase_question(phase, profile),
        },
    ]

    return render_page(profile=profile, phase=phase, history=history)

@app.post("/analyze", response_class=HTMLResponse)
def analyze(category: str = Form(...)):
    profile = blank_profile()
    phase = "product"
    history = [
        {"role": "user", "content": category},
    ]

    profile = apply_message_to_profile(profile, phase, category)
    phase = next_phase(profile)
    history = ask_current_phase(profile, phase, history)

    return render_page(profile=profile, phase=phase, history=history)


def advisor_response(message, result):
    lower = message.lower()
    profile = result.get("strategy_profile", {})
    rec = result["recommendation"]
    summary = result["market_summary"]

    product = clean_value(profile.get("product_query") or result.get("product_query"), "the product")
    customer = clean_value(profile.get("audience"), "the target customer")
    base_price = float(rec["recommended_price"])
    cost_floor = float(profile.get("cost_floor") or 0)

    bundle_price = base_price * 1.15
    premium_bundle_price = base_price * 1.30

    if "why did you recommend" in lower or "why is this the right price" in lower:
        return f"""
**Why this price makes sense**

I recommended **{price(base_price)}** because it balances the confirmed strategy profile with the observed market.

**Market context:**  
The market median is **{price(summary["median_price"])}**, with observed prices from **{price(summary["min_price"])}** to **{price(summary["max_price"])}**.

**Strategy context:**  
This recommendation is shaped by:

- Customer: **{customer}**
- Positioning: **{clean_value(profile.get("positioning"))}**
- Differentiation: **{clean_value(profile.get("differentiation"))}**

**Business logic:**  
The goal is not just to pick the cheapest or highest possible price. The goal is to choose a launch price that customers can understand, that fits the market, and that gives you room to test demand.
"""

    if "bundle" in lower:
        return f"""
**Recommended action: Bundle strategy**

**Base product:** {price(base_price)}

**Starter bundle:** {price(bundle_price)}  
Use this as the main upsell. Include low-cost accessories, setup guidance, or essentials that help {customer} get started faster.

**Premium bundle:** {price(premium_bundle_price)}  
Use this to capture customers with higher willingness to pay. Add stronger accessories, service, support, or a more complete setup.

**Why this works:**  
The base price keeps the product accessible, while bundles lift average order value without weakening the core launch price.

**What to test:**  
Compare base-only conversion against starter-bundle conversion and average order value.
"""

    if "risk" in lower:
        risks = [
            "The competitor data may include products that are not perfect substitutes.",
            "Premium positioning needs clear proof of value, otherwise customers may compare only on price.",
            "A lower price could improve conversion but weaken quality perception.",
            "A higher price could improve revenue per order but reduce early adoption.",
        ]

        if profile.get("cost_floor"):
            risks.append("The cost floor protects margin, but it limits how aggressive growth pricing can be.")

        risk_text = "\n".join([f"- {risk}" for risk in risks])

        return f"""
**Strategic risk review**

The biggest risks for **{product}** are:

{risk_text}

**Most important validation:**  
Before committing to this price, test whether {customer} clearly understand why this product is better, safer, easier, or more specialized than nearby alternatives.

**Decision rule:**  
If conversion is weak but engagement is strong, adjust messaging before cutting price. If conversion is weak and engagement is weak, revisit positioning.
"""

    if "30 days" in lower or "test" in lower or "experiment" in lower:
        low_price = max(base_price * 0.92, cost_floor)
        high_price = base_price * 1.08

        return f"""
**30-day launch test plan**

**Test 1: Price sensitivity**  
Compare **{price(low_price)}**, **{price(base_price)}**, and **{price(high_price)}**.

**Test 2: Messaging**  
Run two versions of the product page:
- Value-focused: emphasizes price-to-quality ratio
- Specialist-focused: emphasizes expertise, reliability, and fit for {customer}

**Test 3: Bundle demand**  
Compare the base product at **{price(base_price)}** against a starter bundle around **{price(bundle_price)}**.

**Metrics to track:**  
Conversion rate, revenue per visitor, average order value, add-to-cart rate, and refund/return rate.

**Best next decision:**  
Keep the price that produces the best revenue per visitor, not just the highest conversion rate.
"""

    if "competitor" in lower or "market" in lower:
        return f"""
**Market read**

The market median is **{price(summary["median_price"])}**, with observed prices from **{price(summary["min_price"])}** to **{price(summary["max_price"])}**.

Your recommended price of **{price(base_price)}** is not just a math output. It should be interpreted through the strategy profile:

- Customer: **{customer}**
- Positioning: **{clean_value(profile.get("positioning"))}**
- Differentiation: **{clean_value(profile.get("differentiation"))}**

**Strategic implication:**  
The main question is not “Are we cheaper than the market?” The better question is whether customers can immediately understand why this product deserves its price compared with nearby alternatives.
"""

    if "discount" in lower:
        discount_price = max(base_price * 0.90, cost_floor)

        return f"""
**Discount recommendation**

I would avoid making a discount the main strategy. A permanent discount can train customers to wait for lower prices.

**Better approach:**  
Launch at **{price(base_price)}**, but test a short intro offer around **{price(discount_price)}**.

**Why:**  
This creates urgency while protecting the long-term reference price.

**Guardrail:**  
Do not discount below your cost floor or below a price that damages perceived quality.
"""

    return generate_business_explanation(
        category=result.get("product_query", "product"),
        market_summary=result["market_summary"],
        recommendation=result["recommendation"],
        objective=result.get("parsed_prompt", {}).get("objective", "maximize_revenue"),
        question=message,
    )


@app.post("/chat", response_class=HTMLResponse)
def chat(
    message: str = Form(...),
    profile: str = Form(""),
    phase: str = Form("product"),
    history: str = Form(""),
    session_id: str = Form(""),
):
    profile_data = decode_json(profile, blank_profile())
    chat_history = decode_json(history, [])

    message = message.strip()
    chat_history.append({"role": "user", "content": message})

    existing_result = RESULT_CACHE.get(session_id) if session_id else None

    if existing_result:
        lower = message.lower()
        revised_profile = profile_data.copy()
        changed_strategy = False
        new_objective = None
        new_positioning = None
        cost_floor = None

        if (
            "compare to the market" in lower
            or "market snapshot" in lower
            or lower == "market"
        ):
            existing_result["active_tab"] = "market"
            RESULT_CACHE[session_id] = existing_result

            chat_history.append({
                "role": "agent",
                "content": "Good question. I opened the Market tab so you can compare the recommendation against the market median, price range, and revenue curve.",
            })

            return render_page(profile_data, "complete", chat_history, session_id, existing_result)

        should_update_strategy = is_strategy_update_request(message)

        if should_update_strategy:
            new_objective = objective_from_text(message)
            if new_objective:
                revised_profile["objective"] = new_objective
                changed_strategy = True

            new_positioning = positioning_from_text(message)
            if new_positioning:
                revised_profile["positioning"] = new_positioning
                changed_strategy = True

            cost_floor = extract_cost_floor(message)
            if cost_floor:
                revised_profile["cost_floor"] = cost_floor
                revised_profile["constraints_answered"] = True
                changed_strategy = True

            if "no hard constraint" in lower or "remove cost floor" in lower:
                revised_profile["cost_floor"] = None
                revised_profile["constraints_answered"] = True
                changed_strategy = True

        if changed_strategy:
            result = run_strategy(revised_profile)

            if result.get("error"):
                chat_history.append({
                    "role": "agent",
                    "content": f"I tried to update the scenario, but ran into this issue: {result['error']}",
                })
                return render_page(revised_profile, "complete", chat_history, session_id, existing_result)

            result["advisor_plan"] = None
            result["active_tab"] = "overview"
            RESULT_CACHE[session_id] = result
            rec = result["recommendation"]

            strategy_change = []

            if revised_profile.get("objective") != profile_data.get("objective"):
                strategy_change.append(
                    f"goal changed to **{objective_label(revised_profile.get('objective'))}**"
                )

            if revised_profile.get("positioning") != profile_data.get("positioning"):
                strategy_change.append(
                    f"positioning changed to **{revised_profile.get('positioning')}**"
                )

            if revised_profile.get("cost_floor") != profile_data.get("cost_floor"):
                if revised_profile.get("cost_floor"):
                    strategy_change.append(
                        f"cost floor set to **{price(revised_profile.get('cost_floor'))}**"
                    )
                else:
                    strategy_change.append("cost floor removed")

            change_text = ", ".join(strategy_change) if strategy_change else "the scenario changed"

            chat_history.append({
                "role": "agent",
                "content": (
                    f"Got it. I updated the strategy because {change_text}.\n\n"
                    f"**Updated recommendation:** {price(rec['recommended_price'])}\n\n"
                    f"Expected revenue is about **{money(rec['expected_revenue'])}/month** "
                    f"at an estimated **{percent(rec['conversion_rate'])} conversion rate**.\n\n"
                    f"I refreshed the dashboard on the right."
                ),
            })

            return render_page(revised_profile, "complete", chat_history, session_id, result)

        if is_advisor_question(message):
            answer = advisor_response(message, existing_result)
            plan = advisor_plan_from_message(message, existing_result)

            if plan:
                existing_result["advisor_plan"] = plan
                existing_result["active_tab"] = "advisor"
                RESULT_CACHE[session_id] = existing_result

            chat_history.append({"role": "agent", "content": answer})
            return render_page(profile_data, "complete", chat_history, session_id, existing_result)

        answer = advisor_response(message, existing_result)
        plan = advisor_plan_from_message(message, existing_result)

        if plan:
            existing_result["advisor_plan"] = plan
            existing_result["active_tab"] = "advisor"
            RESULT_CACHE[session_id] = existing_result

        chat_history.append({"role": "agent", "content": answer})
        return render_page(profile_data, "complete", chat_history, session_id, existing_result)

    if phase == "confirm":
        edit_phase = edit_phase_from_message(message)

        if edit_phase:
            phase = edit_phase
            chat_history = ask_current_phase(profile_data, phase, chat_history)
            return render_page(profile_data, phase, chat_history, session_id)

        if "build" in message.lower() or "looks right" in message.lower():
            result = run_strategy(profile_data)

            if result.get("error"):
                chat_history.append({
                    "role": "agent",
                    "content": f"I ran into an issue: {result['error']}",
                })
                return render_page(profile_data, phase, chat_history)

            result["advisor_plan"] = None
            result["active_tab"] = "overview"
            rec = result["recommendation"]

            chat_history.append({
                "role": "agent",
                "content": (
                    f"Great. I built the launch pricing strategy from the confirmed profile.\n\n"
                    f"**Recommendation:** launch around **{price(rec['recommended_price'])}**.\n\n"
                    f"Expected revenue is about **{money(rec['expected_revenue'])}/month** "
                    f"at an estimated **{percent(rec['conversion_rate'])} conversion rate**.\n\n"
                    f"You can now ask me to pressure-test the strategy, build a bundle, change the goal, or run a what-if scenario."
                ),
            })

            session_id = str(uuid.uuid4())
            RESULT_CACHE[session_id] = result

            return render_page(profile_data, "complete", chat_history, session_id, result)

    

    profile_data = apply_message_to_profile(profile_data, phase, message)
    phase = next_phase(profile_data)

    if phase == "confirm":
        cost_floor_text = (
            price(profile_data["cost_floor"])
            if profile_data.get("cost_floor")
            else "No hard constraint"
        )

        confirm_text = (
            f"Here’s the strategy profile I’ll use:\n\n"
            f"**Product:** {clean_value(profile_data.get('product_query'))}\n\n"
            f"**Customer:** {clean_value(profile_data.get('audience'))}\n\n"
            f"**Positioning:** {clean_value(profile_data.get('positioning'))}\n\n"
            f"**Differentiation:** {clean_value(profile_data.get('differentiation'))}\n\n"
            f"**Goal:** {objective_label(profile_data.get('objective'))}\n\n"
            f"**Cost floor:** {cost_floor_text}\n\n"
            f"Does this look right?"
        )

        chat_history.append({"role": "agent", "content": confirm_text})
        return render_page(profile_data, phase, chat_history, session_id)

    chat_history = ask_current_phase(profile_data, phase, chat_history)

    return render_page(profile_data, phase, chat_history, session_id)


@app.post("/ask", response_class=HTMLResponse)
def ask(
    question: str = Form(...),
    category: str = Form(""),
    history: str = Form(""),
    session_id: str = Form(""),
):
    profile = blank_profile()
    chat_history = decode_json(history, [])
    chat_history.append({"role": "user", "content": question})

    result = RESULT_CACHE.get(session_id)

    if not result:
        chat_history.append({"role": "agent", "content": "I lost the previous pricing analysis. Please start a new strategy setup."})
        return render_page(profile, "product", chat_history)

    answer = generate_business_explanation(
        category=result.get("product_query", "product"),
        market_summary=result["market_summary"],
        recommendation=result["recommendation"],
        objective=result.get("parsed_prompt", {}).get("objective", "maximize_revenue"),
        question=question,
    )

    chat_history.append({"role": "agent", "content": answer})
    return render_page(result.get("strategy_profile", profile), "complete", chat_history, session_id, result)