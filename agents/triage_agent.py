import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a Triage Agent for a SaaS platform support system.
Your job is to analyze an incoming support ticket and output a structured triage assessment.

You must respond ONLY with a valid JSON object in this exact format:
{
  "severity": "P1|P2|P3|P4",
  "category": "api_error|data_sync|auth|performance|compliance|other",
  "summary": "One sentence summary of the issue",
  "affected_components": ["list", "of", "components"],
  "investigation_priority": "immediate|high|medium|low",
  "reasoning": "Brief explanation of your severity and category decision"
}

Severity guide:
- P1: System down, data loss, security breach
- P2: Major feature broken, multiple users affected
- P3: Feature degraded, workaround exists
- P4: Minor issue, cosmetic, single user
"""

def run_triage_agent(ticket_title: str, ticket_description: str) -> dict:
    print("\n🔍 Triage Agent running...")
    
    user_message = f"""
Ticket Title: {ticket_title}

Ticket Description:
{ticket_description}

Analyze this ticket and return the structured triage JSON.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()
    
    # Clean JSON if wrapped in code fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    result = json.loads(raw.strip())
    print(f"✅ Triage complete — Severity: {result['severity']} | Category: {result['category']}")
    return result
