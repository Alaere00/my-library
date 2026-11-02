import numpy as np
import json
from app.book_helpers import book_to_row
from app.schemas.book_model import BookSearchResult
from app.schemas.book_model import BookSearchResult
from app.services.recommendation.candidates import search_hardcover, search_queries
from app.services.embeddings.embeddings import build_text, embed_text, weight
from app.dbs.supabase_db import catalog_client

def _vec(v):
    return np.array(json.loads(v) if isinstance(v, str) else v, dtype=np.float64)


def get_recommendation(user_id: str, limit: int = 25) -> list[dict]:
    shelf = (
        catalog_client.table("user_books")
        .select("status,is_favorite,rating,books(provider_book_id,authors,genres,moods,embedding,description,title,subtitle)")
        .eq("user_id", user_id)
        .execute().data
    )

    shelved = {r["books"]["provider_book_id"] for r in shelf if r.get("books")}
    vecs, weights, liked = [], [], []
    for r in shelf:
        b, w = r.get("books") or {}, weight(r)
        if b.get("embedding") is not None and w > 0:
            vecs.append(_vec(b["embedding"]))
            weights.append(w)
            liked.append(b)

    if not vecs:
        return []

    taste = np.average(np.stack(vecs), axis=0, weights=weights)
    taste /= np.linalg.norm(taste)

    seen, candidates = set(shelved), []
    for q in search_queries(liked):
        for b in search_hardcover(q, per_page=limit):
            pid = str(b.id)
            if pid in seen or not b.description:
                continue

            seen.add(pid)
            candidates.append(b)

    if not candidates:
        return BookSearchResult(hits=[])


    similarities = embed_text([build_text(book_to_row(c)) for c in candidates]) @ taste
    top = np.argsort(similarities)[:limit]

    return BookSearchResult(hits=[candidates[i] for i in top], found=len(top), page=1, per_page=limit, total_pages=len(candidates))