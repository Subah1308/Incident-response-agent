import anthropic
import json
import os
from core.scratchpad import IncidentScratchpad
from core.rag import search_similar_incidents

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are the Root Cause Agent in an autonomous SaaS incident response system.
You receive findings from the Triage and Log Analyst agents, PLUS similar past incidents retrieved
from a knowledge base (RAG). Use all this context to hypothesize the most likely root cause.

Respond ONLY in valid JSON with keys:
- root_cause_hypothesis (string): your best explanation of what caused this incident
- confidence_score (float 0.0-1.0): how confident you are
- reasoning (string): brief explanation of your reasoning

No explanation, no markdown, just the JSON object."""


def run(scratchpad: IncidentScratchpad) -> IncidentScratchpad:
    print(f"\n🧠 Root Cause Agent running (with RAG)...")

    # RAG: search for similar past incidents
    search_query = f"{scratchpad.ticket_title} {scratchpad.category} {' '.join(scratchpad.error_patterns or [])}"
    similar = search_similar_incidents(search_query, top_k=3)
    scratchpad.similar_past_incidents = similar

    print(f"   Retrieved {len(similar)} similar past incidents from knowledge base")

    # Format past incidents for context
    past_context = ""
    for i, inc in enumerate(similar, 1):
        past_context += f"\nPast Incident {i}:\n"
        past_context += f"  Title: {inc.get('title')}\n"
        past_context += f"  Root Cause: {inc.get('root_cause')}\n"
        past_context += f"  Resolution: {inc.get('resolution')}\n"

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=768,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Ticket: {scratchpad.ticket_title}\n"
                    f"Category: {scratchpad.category} | Severity: {scratchpad.severity}\n\n"
                    f"Log Anomalies: {scratchpad.log_anomalies}\n"
                    f"Error Patterns: {scratchpad.error_patterns}\n"
                    f"Affected Services: {scratchpad.affected_services}\n\n"
                    f"--- Similar Past Incidents (from knowledge base) ---{past_context}"
                )
            }
        ]
    )

    raw = response.content[0].text.strip()
    result = json.loads(raw)

    scratchpad.root_cause_hypothesis = result.get("root_cause_hypothesis")
    scratchpad.confidence_score = result.get("confidence_score")

    print(f"   Root cause identified (confidence: {scratchpad.confidence_score:.0%})")
    return scratchpad
