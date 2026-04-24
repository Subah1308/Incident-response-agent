import json
from core.supabase_client import get_supabase_client
from agents.triage_agent import run_triage_agent
from agents.log_analyst_agent import run_log_analyst_agent
from agents.root_cause_agent import run_root_cause_agent
from agents.resolution_agent import run_resolution_agent

def run_incident_pipeline(ticket_title: str, ticket_description: str) -> dict:
    """
    Orchestrates all 4 agents in sequence:
    Triage → Log Analysis → Root Cause (RAG) → Resolution
    Saves everything to Supabase.
    """
    print(f"\n{'='*60}")
    print(f"🚨 INCIDENT PIPELINE STARTED")
    print(f"Ticket: {ticket_title}")
    print(f"{'='*60}")

    supabase = get_supabase_client()

    # Save ticket to Supabase
    ticket_response = supabase.table("tickets").insert({
        "title": ticket_title,
        "description": ticket_description
    }).execute()
    ticket_id = ticket_response.data[0]["id"]
    print(f"\n📝 Ticket saved to Supabase (ID: {ticket_id})")

    # Shared incident scratchpad - agents read/write to this
    scratchpad = {
        "ticket_id": ticket_id,
        "ticket_title": ticket_title,
        "ticket_description": ticket_description,
    }

    # Agent 1: Triage
    triage_result = run_triage_agent(ticket_title, ticket_description)
    scratchpad["triage"] = triage_result

    # Agent 2: Log Analysis
    log_result = run_log_analyst_agent(ticket_description, triage_result)
    scratchpad["log_analysis"] = log_result

    # Agent 3: Root Cause (with RAG)
    root_cause_result, similar_incidents = run_root_cause_agent(
        ticket_description, triage_result, log_result
    )
    scratchpad["root_cause"] = root_cause_result
    scratchpad["similar_incidents"] = similar_incidents

    # Agent 4: Resolution
    resolution_result = run_resolution_agent(
        ticket_title, triage_result, log_result, root_cause_result
    )
    scratchpad["resolution"] = resolution_result

    # Save full incident report to Supabase
    supabase.table("incident_reports").insert({
        "ticket_id": ticket_id,
        "severity": triage_result["severity"],
        "category": triage_result["category"],
        "triage_output": triage_result,
        "log_analysis_output": log_result,
        "root_cause_output": root_cause_result,
        "resolution_output": resolution_result,
        "similar_incidents": similar_incidents
    }).execute()

    print(f"\n{'='*60}")
    print(f"✅ INCIDENT PIPELINE COMPLETE — Saved to Supabase")
    print(f"{'='*60}\n")

    return scratchpad
