import httpx
import json
from typing import Counter
from fastapi import Query
from app.schemas.book_model import BookInfo
from app.schemas.bookshelf_model import Status
from app.schemas.hardcover_api_schema import search_query
from app import settings



def search_hardcover(query: str, per_page: int = Query(20, ge=1, le=50)) -> list[BookInfo]:

    r = httpx.post(settings.hardcover_api_url, 
            json={"query": search_query , "variables": {"q": query, "page": 1, "per_page": per_page }},
            headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"}, timeout=10.0)
                
    data = r.json()
    res = data["data"]["search"]["results"]
    if isinstance(res, str):
        res = json.loads(res)

    return BookInfo.model_validate([hit["document"] for hit in res["hits"]])


def search_queries(liked: list[dict]) -> list[str]:
    genres = Counter(g for b in liked for g in b.get("genres", []))
    authors = Counter(a for b in liked for a in b.get("authors", []))
    queries = [g for g, _ in genres.most_common(5)] + [a for a, _ in authors.most_common(5)]
    return list(dict.fromkeys(queries)) 
