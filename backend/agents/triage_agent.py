import anthropic
import json
import os
from core.scratchpad import IncidentScratchpad

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are the Triage Agent in an autonomous SaaS incident response system.
Your job is to read an incoming support ticket and determine:
1. Severity: P1 (critical/down), P2 (major degradation), P3 (minor issue), P4 (question/low impact)
2. Category: one of [API Failure, Data Sync Error, Authentication Issue, Report Generation, Performance Degradation, Configuration Error, Other]
3. Investigation path: a concise instruction for the next agent on what to look for in the logs

Respond ONLY in valid JSON with keys: severity, category, investigation_path.
No explanation, no markdown, just the JSON object."""


def run(scratchpad: IncidentScratchpad) -> IncidentScratchpad:
    print(f"\n🔍 Triage Agent running on ticket: {scratchpad.ticket_id}")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Ticket Title: {scratchpad.ticket_title}\n\nDescription: {scratchpad.ticket_description}"
            }
        ]
    )

    raw = response.content[0].text.strip()
    result = json.loads(raw)

    scratchpad.severity = result.get("severity")
    scratchpad.category = result.get("category")
    scratchpad.investigation_path = result.get("investigation_path")

    print(f"   Severity: {scratchpad.severity} | Category: {scratchpad.category}")
    return scratchpad
