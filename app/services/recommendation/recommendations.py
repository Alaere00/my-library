import numpy as np
from sympy import per

from app.book_helpers import book_to_row
from app.schemas.book_model import BookSearchResult
from app.schemas.book_model import BookSearchResult
from candidates import search_hardcover, search_queries
from embeddings.embeddings import build_text, embed_text, _weight
from app.dbs.supabase_db import catalog_client

def get_recommendation(user_id: str, limit: int = 25) -> list[dict]:
    shelf = (
        catalog_client.table("user_books")
        .select("status, is_favorite, rating, books(provider_book_id, authors, genres, moods, embeddings, description, title, subtitle)")
        .eq("user_id", user_id)
        .execute().data
    )

    shelved = {r["books"]["provider_book_id"] for r in shelf if r["status"] == "read" and r["books"]["embeddings"]}
    vecs, weights, liked = [], [], []
    for r in shelf:
        b, w = r.get("book") or {}, _weight(r)
        if b.get("embedding") is not None and w > 0:
            vecs.append(b.get("embeddings"))
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

    if not candidates:
        return BookSearchResult(hits=[])


    similarities = embed_text([build_text(book_to_row(c)) for c in candidates]) @ taste
    top = np.argsort(similarities)[:limit]

    return BookSearchResult(hits=[candidates[i] for i in top], found=len(top), page=1, per_page=limit, total_pages=len(candidates))