import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a Resolution Agent for a SaaS platform support system.
You receive the full incident analysis from other agents and produce two outputs:
1. A customer-facing response (clear, professional, empathetic)
2. An internal engineering handoff (technical, actionable)

You must respond ONLY with a valid JSON object in this exact format:
{
  "customer_response": {
    "subject": "Email subject line",
    "body": "Professional customer-facing message acknowledging the issue, current status, and next steps"
  },
  "engineering_handoff": {
    "priority": "P1|P2|P3|P4",
    "title": "Short technical title",
    "root_cause": "Technical root cause description",
    "steps_to_reproduce": ["step 1", "step 2"],
    "investigation_checklist": ["item 1", "item 2", "item 3"],
    "suggested_fix": "Suggested fix or workaround",
    "affected_components": ["component 1", "component 2"]
  },
  "resolution_confidence": "high|medium|low",
  "estimated_fix_time": "e.g. 2-4 hours, 1-2 days"
}
"""

def run_resolution_agent(ticket_title: str, triage_result: dict, log_result: dict, root_cause_result: dict) -> dict:
    print("\n✍️  Resolution Agent running...")

    user_message = f"""
TICKET TITLE: {ticket_title}

TRIAGE:
{json.dumps(triage_result, indent=2)}

LOG ANALYSIS:
{json.dumps(log_result, indent=2)}

ROOT CAUSE ANALYSIS:
{json.dumps(root_cause_result, indent=2)}

Generate the customer response and engineering handoff report.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw.strip())
    print(f"✅ Resolution package generated — Fix time estimate: {result['estimated_fix_time']}")
    return result
