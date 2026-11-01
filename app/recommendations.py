


from fastapi import HTTPException, Query
import httpx
from app.schemas.book_model import BookInfo
from app.schemas.bookshelf_model import Status
from app.schemas.hardcover_api_schema import search_query
from app import settings


async def search_hardcover(query: str, per_page: int = Query(20, ge=1, le=50)) -> list[BookInfo]:

        r = httpx.post(settings.hardcover_api_url, 
            json={"query": search_query , "variables": {"q": query, "page": 1, "per_page": per_page }},
            headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"}, timeout=10.0)
                
    data = response.json()
    res = data["data"]["search"]["results"]
    if isinstance(res, str):
        res = json.loads(res)

    return BookSearchResult(found=res["found"], hits=[BookInfo.model_validate(hit["document"]) for hit in res["hits"]], page=res["page"], per_page=per_page, total_pages=math.ceil(res["found"]/per_page))