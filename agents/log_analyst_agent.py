import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a Log Analyst Agent for a SaaS platform support system.
Your job is to analyze error logs and identify patterns, anomalies, and key signals.

You must respond ONLY with a valid JSON object in this exact format:
{
  "error_patterns": ["list of recurring error types found"],
  "anomalies": ["list of unusual behaviors or spikes detected"],
  "affected_services": ["services or endpoints involved"],
  "error_frequency": "description of how often errors are occurring",
  "timeline": "when did the issue start based on logs",
  "key_signals": ["most important clues for root cause investigation"],
  "log_summary": "2-3 sentence plain English summary of what the logs show"
}
"""

def run_log_analyst_agent(ticket_description: str, triage_result: dict) -> dict:
    print("\n📋 Log Analyst Agent running...")

    user_message = f"""
Ticket Description: {ticket_description}

Triage Assessment:
- Severity: {triage_result['severity']}
- Category: {triage_result['category']}
- Affected Components: {', '.join(triage_result['affected_components'])}

Based on this ticket context, analyze what the logs likely show.
Generate a realistic log analysis as if you had reviewed actual system logs
for a SaaS supply chain compliance platform.

Return the structured log analysis JSON.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw.strip())
    print(f"✅ Log analysis complete — {len(result['error_patterns'])} error patterns found")
    return result
