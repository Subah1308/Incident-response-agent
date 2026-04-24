import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.orchestrator import run_incident_pipeline
from core.supabase_client import get_supabase_client

app = FastAPI(title="Incident Response Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TicketRequest(BaseModel):
    title: str
    description: str

@app.post("/api/analyze")
def analyze_ticket(request: TicketRequest):
    """Run the full 4-agent pipeline on a support ticket."""
    result = run_incident_pipeline(request.title, request.description)
    return result

@app.get("/api/reports")
def get_reports():
    """Fetch all past incident reports from Supabase."""
    supabase = get_supabase_client()
    response = supabase.table("incident_reports")\
        .select("*, tickets(title, description)")\
        .order("created_at", desc=True)\
        .limit(20)\
        .execute()
    return response.data

@app.get("/api/health")
def health():
    return {"status": "ok"}
