from sentence_transformers import SentenceTransformer
from db.supabase_client import get_supabase
from typing import List

# Load embedding model once at startup (runs locally, no API cost)
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print("Loading embedding model (first time only)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim, fast, free
    return _model


def embed_text(text: str) -> List[float]:
    """Convert text to a vector embedding."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def search_similar_incidents(query: str, top_k: int = 3) -> List[dict]:
    """
    RAG: Given a query string, find the most semantically similar
    past incidents from the Supabase knowledge base.
    """
    supabase = get_supabase()
    query_embedding = embed_text(query)

    # Call the pgvector similarity search function in Supabase
    result = supabase.rpc(
        "match_incidents",
        {
            "query_embedding": query_embedding,
            "match_count": top_k
        }
    ).execute()

    return result.data or []


def store_incident_knowledge(title: str, description: str, root_cause: str, resolution: str):
    """
    After resolving an incident, store it in the knowledge base
    so future incidents can learn from it (RAG feedback loop).
    """
    supabase = get_supabase()
    combined_text = f"{title} {description} {root_cause}"
    embedding = embed_text(combined_text)

    supabase.table("incident_knowledge").insert({
        "title": title,
        "description": description,
        "root_cause": root_cause,
        "resolution": resolution,
        "embedding": embedding
    }).execute()
    print(f"Stored incident '{title}' in knowledge base.")
