import anthropic
import json
import os
from core.scratchpad import IncidentScratchpad

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are the Resolution Agent in an autonomous SaaS incident response system.
You receive the complete incident analysis from all previous agents. Your job is to produce:

1. customer_facing_summary: A clear, empathetic, non-technical summary for the customer (2-3 sentences)
2. internal_eng_report: A detailed technical report for the engineering team including root cause, affected services, and evidence
3. recommended_actions: A list of concrete next steps (e.g. "Restart auth service", "Check DB connection pool limits")
4. escalate_to_engineering: true if this needs immediate engineering attention, false otherwise

Respond ONLY in valid JSON with those four keys. No markdown, no explanation."""


def run(scratchpad: IncidentScratchpad) -> IncidentScratchpad:
    print(f"\n✍️  Resolution Agent generating reports...")

    similar_refs = ""
    for inc in (scratchpad.similar_past_incidents or []):
        similar_refs += f"- {inc.get('title')}: resolved by {inc.get('resolution')}\n"

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Ticket: {scratchpad.ticket_title}\n"
                    f"Severity: {scratchpad.severity} | Category: {scratchpad.category}\n\n"
                    f"Log Anomalies: {scratchpad.log_anomalies}\n"
                    f"Error Patterns: {scratchpad.error_patterns}\n"
                    f"Affected Services: {scratchpad.affected_services}\n\n"
                    f"Root Cause: {scratchpad.root_cause_hypothesis}\n"
                    f"Confidence: {scratchpad.confidence_score}\n\n"
                    f"Similar Past Incidents:\n{similar_refs or 'None found'}"
                )
            }
        ]
    )

    raw = response.content[0].text.strip()
    result = json.loads(raw)

    scratchpad.customer_facing_summary = result.get("customer_facing_summary")
    scratchpad.internal_eng_report = result.get("internal_eng_report")
    scratchpad.recommended_actions = result.get("recommended_actions", [])
    scratchpad.escalate_to_engineering = result.get("escalate_to_engineering", False)

    print(f"   Reports generated | Escalate to engineering: {scratchpad.escalate_to_engineering}")
    return scratchpad
