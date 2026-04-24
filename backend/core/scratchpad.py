from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class IncidentScratchpad(BaseModel):
    """
    Shared state object passed between all agents.
    Each agent reads from this and adds its findings.
    This is the 'agentic memory' of the system.
    """
    # Input
    ticket_id: str
    ticket_title: str
    ticket_description: str
    raw_logs: Optional[str] = None
    submitted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Triage Agent output
    severity: Optional[str] = None           # P1, P2, P3, P4
    category: Optional[str] = None           # e.g. "API Failure", "Data Sync", "Auth"
    investigation_path: Optional[str] = None # what to investigate next

    # Log Analyst Agent output
    log_anomalies: Optional[List[str]] = None
    error_patterns: Optional[List[str]] = None
    affected_services: Optional[List[str]] = None

    # Root Cause Agent output (RAG-powered)
    similar_past_incidents: Optional[List[dict]] = None
    root_cause_hypothesis: Optional[str] = None
    confidence_score: Optional[float] = None

    # Resolution Agent output
    customer_facing_summary: Optional[str] = None
    internal_eng_report: Optional[str] = None
    recommended_actions: Optional[List[str]] = None
    escalate_to_engineering: Optional[bool] = None
