from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_text(b: dict) -> str:
    join = lambda k: ". ".join(b.get(k) or [])
    title = (b.get("title") or "") + (f": {b['subtitle']}" if b.get("subtitle") else "")
    return (f"{title} by {join('authors')}. Genres: {join('genres')}. "
            f"Moods: {join('moods')}. Tags: {join('tags')}. {b.get('description') or ''}")

def embed_text(texts: list[str]):
    return model.encode(texts, normalize_embeddings=True)

def weight(row: dict) -> float:
    rating = row.get("rating")

    if row["status"] == "did_not_complete" or (rating is not None and rating < 2):
        return 0.0

    w = 1.0
    if row["status"] == "completed":
        w+= 1.0
    if row["is_favorite"]:
        w+= 2.0
    if (rating or 0) >= 4:
        w+= 1.0

    return w


