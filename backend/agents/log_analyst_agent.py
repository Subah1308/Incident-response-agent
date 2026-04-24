import anthropic
import json
import os
from core.scratchpad import IncidentScratchpad

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are the Log Analyst Agent in an autonomous SaaS incident response system.
You receive raw application logs and an investigation hint from the Triage Agent.
Your job is to extract:
1. log_anomalies: list of specific anomalies found (e.g. "503 errors spike at 14:32 UTC")
2. error_patterns: recurring patterns (e.g. "DB connection timeout every ~30s")
3. affected_services: which services or components are involved

Respond ONLY in valid JSON with keys: log_anomalies (list), error_patterns (list), affected_services (list).
No explanation, no markdown, just the JSON object."""


def run(scratchpad: IncidentScratchpad) -> IncidentScratchpad:
    print(f"\n📋 Log Analyst Agent running...")

    logs_content = scratchpad.raw_logs or "No logs provided. Infer from ticket description."

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=768,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Investigation focus: {scratchpad.investigation_path}\n\n"
                    f"Ticket: {scratchpad.ticket_title}\n\n"
                    f"Logs:\n{logs_content}"
                )
            }
        ]
    )

    raw = response.content[0].text.strip()
    result = json.loads(raw)

    scratchpad.log_anomalies = result.get("log_anomalies", [])
    scratchpad.error_patterns = result.get("error_patterns", [])
    scratchpad.affected_services = result.get("affected_services", [])

    print(f"   Found {len(scratchpad.log_anomalies)} anomalies in {len(scratchpad.affected_services)} services")
    return scratchpad
