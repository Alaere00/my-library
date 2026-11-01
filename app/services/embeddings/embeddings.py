from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_text(b: dict) -> str:
    join = lambda k: ". ".join(b.get(k) or [])
    title = (b.get("title") or "") + (f": {b["subtitle"]}" if b.get("subtitle") else "")
    return (f"{title} by {"".join(b["authors"])}. Genres: {join('genres')}. "
            f"Moods: {join('moods')}. Tags: {join("tags")}. {b["description"] or ''}"
            )

def embed_text(texts: list[str]):
    return model.encode(texts, normalize_embeddings=True)