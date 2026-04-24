import os
import json
import anthropic
from dotenv import load_dotenv
from core.embeddings import embed_text
from core.supabase_client import get_supabase_client

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a Root Cause Analysis Agent for a SaaS platform support system.
You have access to findings from a triage agent, log analysis, and similar past incidents retrieved from a knowledge base.

Your job is to synthesize all available information and determine the most likely root cause.

You must respond ONLY with a valid JSON object in this exact format:
{
  "root_cause": "Clear, specific description of the root cause",
  "confidence": "high|medium|low",
  "contributing_factors": ["list of factors that led to this issue"],
  "similar_past_incidents": ["titles of similar incidents from knowledge base"],
  "code_investigation_hints": ["specific areas of code or config to inspect"],
  "is_known_issue": true or false,
  "known_issue_reference": "reference if known, else null",
  "rca_summary": "3-4 sentence plain English root cause summary"
}
"""

def retrieve_similar_incidents(query_text: str) -> list:
    """RAG: embed the query and retrieve semantically similar past incidents from Supabase."""
    print("  🔎 RAG: Searching knowledge base for similar incidents...")
    
    supabase = get_supabase_client()
    query_embedding = embed_text(query_text)
    
    response = supabase.rpc("match_knowledge_base", {
        "query_embedding": query_embedding,
        "match_threshold": 0.4,
        "match_count": 3
    }).execute()
    
    results = response.data or []
    print(f"  ✅ RAG: Found {len(results)} similar past incidents")
    return results

def run_root_cause_agent(ticket_description: str, triage_result: dict, log_result: dict) -> tuple[dict, list]:
    print("\n🧠 Root Cause Agent running (with RAG)...")

    # RAG — retrieve similar past incidents from Supabase
    rag_query = f"{ticket_description} {triage_result['category']} {' '.join(log_result['key_signals'])}"
    similar_incidents = retrieve_similar_incidents(rag_query)

    # Format RAG context for the agent
    rag_context = ""
    if similar_incidents:
        rag_context = "\n\nSIMILAR PAST INCIDENTS FROM KNOWLEDGE BASE:\n"
        for i, incident in enumerate(similar_incidents, 1):
            rag_context += f"""
Incident {i} (similarity: {incident.get('similarity', 0):.2f}):
- Title: {incident['title']}
- Description: {incident['content']}
- Resolution: {incident.get('resolution', 'N/A')}
"""
    else:
        rag_context = "\n\nNo similar past incidents found in knowledge base.\n"

    user_message = f"""
TICKET: {ticket_description}

TRIAGE FINDINGS:
{json.dumps(triage_result, indent=2)}

LOG ANALYSIS FINDINGS:
{json.dumps(log_result, indent=2)}

{rag_context}

Using all of the above, determine the root cause and return the structured JSON.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw.strip())
    print(f"✅ Root cause identified — Confidence: {result['confidence']}")
    return result, similar_incidents
