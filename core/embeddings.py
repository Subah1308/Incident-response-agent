from sentence_transformers import SentenceTransformer

# Load once at startup — model runs locally, no API key needed
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model (first time only, ~30 seconds)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model ready.")
    return _model

def embed_text(text: str) -> list[float]:
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
