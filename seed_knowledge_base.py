"""
Run this once to populate your Supabase knowledge base with sample past incidents.
This enables the RAG component of the Root Cause Agent.

Usage: python3 seed_knowledge_base.py
"""

from core.supabase_client import get_supabase_client
from core.embeddings import embed_text

PAST_INCIDENTS = [
    {
        "title": "API rate limit exceeded causing supplier data sync failures",
        "content": "Supplier data sync jobs began failing at 02:00 UTC. API gateway logs showed 429 Too Many Requests errors. The nightly batch job was reconfigured without throttling controls.",
        "category": "api_error",
        "resolution": "Implemented exponential backoff and rate limiting on batch sync jobs. Added circuit breaker pattern to prevent cascade failures."
    },
    {
        "title": "OAuth token expiry causing silent authentication failures",
        "content": "Users reported intermittent login failures. Tokens were expiring without proper refresh logic. Affected users in APAC region where session duration is shorter.",
        "category": "auth",
        "resolution": "Fixed token refresh logic. Added proactive token renewal 5 minutes before expiry. Deployed hotfix to production."
    },
    {
        "title": "Compliance report export timing out for large supplier datasets",
        "content": "REACH compliance reports failing for customers with >500 suppliers. Database query was performing full table scan. No pagination in export pipeline.",
        "category": "performance",
        "resolution": "Added database index on supplier_id and compliance_type. Implemented streaming pagination for large exports. Query time reduced from 45s to 1.2s."
    },
    {
        "title": "Webhook delivery failures due to SSL certificate mismatch",
        "content": "Customer webhook endpoints not receiving notifications. SSL handshake errors in outbound webhook service. Certificate validation was too strict for self-signed customer certs.",
        "category": "api_error",
        "resolution": "Added configurable SSL validation option per webhook endpoint. Improved error messaging to customers about SSL requirements."
    },
    {
        "title": "Data sync stuck in pending state after database migration",
        "content": "After a schema migration, sync jobs entered a pending state and never completed. The migration added a NOT NULL column without a default value, breaking insert operations.",
        "category": "data_sync",
        "resolution": "Rolled back migration, added default value to new column, re-ran migration. Added migration validation checks to CI pipeline."
    },
    {
        "title": "Supplier portal showing stale compliance data after cache not invalidated",
        "content": "Suppliers seeing outdated compliance status after manufacturer updated requirements. Redis cache TTL set too high (24 hours). Cache invalidation event was not triggered on compliance update.",
        "category": "data_sync",
        "resolution": "Fixed cache invalidation to trigger on compliance record updates. Reduced TTL to 15 minutes. Added cache-busting for compliance-critical views."
    },
    {
        "title": "Performance degradation during peak hours due to N+1 query issue",
        "content": "Dashboard load times increased from 800ms to 12s during business hours. APM traces showed hundreds of individual database queries per request. ORM lazy loading triggered N+1 on supplier list view.",
        "category": "performance",
        "resolution": "Replaced lazy loading with eager loading using JOIN queries. Implemented query result caching. Response times returned to normal."
    },
    {
        "title": "Bulk import failing silently for CSV files with special characters",
        "content": "Customers reported bulk supplier imports appearing to succeed but data not appearing. CSV parser failing on non-UTF8 characters. Error swallowed without user notification.",
        "category": "data_sync",
        "resolution": "Added UTF-8 encoding validation at upload. Improved error reporting to surface parsing failures. Added support for common encodings (Latin-1, Windows-1252)."
    }
]

def seed():
    supabase = get_supabase_client()
    print(f"Seeding {len(PAST_INCIDENTS)} past incidents into knowledge base...\n")

    for i, incident in enumerate(PAST_INCIDENTS, 1):
        # Embed the title + content together for best semantic search
        text_to_embed = f"{incident['title']}. {incident['content']}"
        embedding = embed_text(text_to_embed)

        supabase.table("knowledge_base").insert({
            "title": incident["title"],
            "content": incident["content"],
            "category": incident["category"],
            "resolution": incident["resolution"],
            "embedding": embedding
        }).execute()

        print(f"✅ [{i}/{len(PAST_INCIDENTS)}] Inserted: {incident['title'][:60]}...")

    print(f"\n🎉 Knowledge base seeded successfully!")
    print("Your RAG system is ready.")

if __name__ == "__main__":
    seed()
