import uuid
from dotenv import load_dotenv
load_dotenv()

from core.scratchpad import IncidentScratchpad
from agents import triage_agent, log_analyst_agent, root_cause_agent, resolution_agent
from db.supabase_client import get_supabase

def run_incident_pipeline(
    ticket_title: str,
    ticket_description: str,
    raw_logs: str = None
) -> IncidentScratchpad:
    """
    Orchestrates the 4-agent pipeline:
    Triage → Log Analyst → Root Cause (RAG) → Resolution

    Each agent receives the shared scratchpad, enriches it, and passes it on.
    """
    print("\n" + "="*60)
    print("🚨 INCIDENT RESPONSE SYSTEM ACTIVATED")
    print("="*60)

    # Initialize shared scratchpad
    scratchpad = IncidentScratchpad(
        ticket_id=f"INC-{str(uuid.uuid4())[:8].upper()}",
        ticket_title=ticket_title,
        ticket_description=ticket_description,
        raw_logs=raw_logs
    )

    print(f"Incident ID: {scratchpad.ticket_id}")

    # Agent pipeline
    scratchpad = triage_agent.run(scratchpad)
    scratchpad = log_analyst_agent.run(scratchpad)
    scratchpad = root_cause_agent.run(scratchpad)
    scratchpad = resolution_agent.run(scratchpad)

    # Persist full incident to Supabase
    _save_to_supabase(scratchpad)

    print("\n" + "="*60)
    print("✅ INCIDENT RESPONSE COMPLETE")
    print("="*60)

    return scratchpad


def _save_to_supabase(scratchpad: IncidentScratchpad):
    """Save the completed incident analysis to Supabase."""
    supabase = get_supabase()
    supabase.table("incidents").insert({
        "ticket_id": scratchpad.ticket_id,
        "ticket_title": scratchpad.ticket_title,
        "ticket_description": scratchpad.ticket_description,
        "severity": scratchpad.severity,
        "category": scratchpad.category,
        "log_anomalies": scratchpad.log_anomalies,
        "error_patterns": scratchpad.error_patterns,
        "affected_services": scratchpad.affected_services,
        "root_cause_hypothesis": scratchpad.root_cause_hypothesis,
        "confidence_score": scratchpad.confidence_score,
        "customer_facing_summary": scratchpad.customer_facing_summary,
        "internal_eng_report": scratchpad.internal_eng_report,
        "recommended_actions": scratchpad.recommended_actions,
        "escalate_to_engineering": scratchpad.escalate_to_engineering,
        "submitted_at": scratchpad.submitted_at
    }).execute()
    print(f"\n💾 Incident saved to Supabase: {scratchpad.ticket_id}")
