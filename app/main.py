import json
import math
import httpx
from fastapi import FastAPI, HTTPException, Depends, Header, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.book_helpers import book_to_row, to_book_info
from app.schemas.book_model import AddToShelfRequest, AuthorInfo, BookInfo, BookSearchResult, Ratings
from app.schemas.bookshelf_model import FavoriteUpdate
from app.services.recommendation.recommendations import get_recommendation
from app.settings import settings
from app.schemas.auth_model import LoginCredentials, UserProfile
from app.schemas.hardcover_api_schema import author_query, title_query, search_query, isbn_query, to_slug
from app.dbs.supabase_db import get_bookshelf, get_secure_data_or_refresh, set_book_status_in_bookshelf, set_favorite_book, set_ratings_in_bookshelf, user_logout, user_sign_up, user_login, create_user_profile, get_current_user_id
# from app.services.embeddings.embeddings import get_book_embeddings
import isbnlib 


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows specific origins
    allow_credentials=True,           # Allows cookies and headers
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allows all headers
)

bearer_scheme = HTTPBearer()

@app.get("/healthz")
def read_root():
    return {"message": "Hello World"}


@app.get("/search/general", response_model=BookSearchResult)
async def search_books(query: str, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=50)) -> BookSearchResult:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.hardcover_api_url, 
                json={"query": search_query , "variables": {"q": query, "page": page, "per_page": per_page }},
                headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"})
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Hardcover API is unavailable: {e}")
    

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Error")
    data = response.json()
    res = data["data"]["search"]["results"]
    if isinstance(res, str):
        res = json.loads(res)

    return BookSearchResult(found=res["found"], hits=[BookInfo.model_validate(hit["document"]) for hit in res["hits"]], page=res["page"], per_page=per_page, total_pages=math.ceil(res["found"]/per_page))


@app.get("/search/title/{book_title}", response_model=BookSearchResult)
async def get_book_by_title(book_title: str, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=50)) -> BookSearchResult:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.hardcover_api_url, 
                json={"query": title_query , "variables": {"title": book_title, "page": page, "per_page": per_page}},
                headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"})
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Hardcover API is unavailable: {e}")
    

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Hardcover returned {response.status_code}: {response.text[:500]}")

    data = response.json()
    res = data["data"]["search"]["results"]
    if isinstance(res, str):
        res = json.loads(res)

    return BookSearchResult(found=res["found"], hits=[BookInfo.model_validate(hit["document"]) for hit in res["hits"]], page=res["page"], per_page=per_page, total_pages=math.ceil(res["found"]/per_page))



@app.get("/search/author/{author_name}", response_model=BookSearchResult)
async def get_author_info(author_name: str, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=50)):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.hardcover_api_url, 
                json={"query": author_query , "variables": {"slug": to_slug(author_name), "limit": per_page, "offset": (page - 1) * per_page}},
                headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"})
                

        response.raise_for_status()
 

    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Hardcover API is unavailable: {e}")
    
    data = response.json()["data"]
    authors = data["authors"]
    if not authors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    total = data["books_aggregate"]["aggregate"]["count"]

    return BookSearchResult(hits=[to_book_info(b, [authors[0]["name"]]) for b in data["books"]], author=AuthorInfo(**data["authors"][0]), page=page, per_page=per_page, found=total, total_pages=math.ceil(total/ per_page) if total else 0)


@app.get("/search/isbn/{isbn}", response_model=BookSearchResult)
async def get_book_info_by_isbn(isbn: str):
    isbn = isbnlib.canonical(isbn)

    if not (isbnlib.is_isbn10(isbn) or isbnlib.is_isbn13(isbn)):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid ISBN")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.hardcover_api_url, 
                json={"query": isbn_query , "variables": {"isbn": isbn }},
                headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"})
                

    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Hardcover API is unavailable: {e}")
    
    if response.status_code != 200:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail="Hardcover API error")

    payload = response.json()

    books = (payload.get("data") or {}).get("books")

    return BookSearchResult(found=len(books), hits=[to_book_info(b) for b in books], page=1, per_page=len(books), total_pages=1)
  
@app.get('/my-bookshelf/profile')
async def get_user_profile(response: Response, authorization: str = Header(None), x_refresh_token: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Missing or malformed Authorization header"
        )
    
    access_token = authorization.split(" ")[1]
    return await get_secure_data_or_refresh(response, access_token=access_token, refresh_token=x_refresh_token)


@app.post('/my-bookshelf/sign-up')
async def create_new_user(email: str, password: str):
    new_user = await user_sign_up(email, password)
    return new_user


@app.post('/my-bookshelf/login')
async def login_user(login_credentials: LoginCredentials):
    logged_in = await user_login(login_credentials)
    return logged_in


@app.post('/my-bookshelf/logout')
async def logout_user():
    return await user_logout()


@app.post('/my-bookshelf/update-profiles')
async def update_user_profile(update_data: UserProfile, user_id: str = Depends(get_current_user_id),
                              authorization=Header(None)
                              ):
    try:
        update = await create_user_profile(user_id=user_id,
                                           first_name=update_data.first_name,
                                           last_name=update_data.last_name,   
                                  )
        return update

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    

@app.get("/my-bookshelf")
def get_user_bookshelf(user_ID: str = Depends(get_current_user_id), credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return get_bookshelf(
        user_id=user_ID,
        access_token=credentials.credentials
    )

    
@app.post("/my-bookshelf/set-status")
def set_book_status(request: AddToShelfRequest, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), user_ID: str = Depends(get_current_user_id)):
    return set_book_status_in_bookshelf(
        user_id=user_ID,
        catalog_book=book_to_row(request.book),
        status=request.status,
        access_token=credentials.credentials
    )


@app.patch("/my-bookshelf/{provider_book_id}/rating")
def rate_book(provider_book_id: str, rating: Ratings, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), user_id: str = Depends(get_current_user_id)):
    row = set_ratings_in_bookshelf(
        provider_book_id=provider_book_id,
        user_id=user_id,
        rating=rating.rating,
        access_token=credentials.credentials
    )

    if not row:
        raise HTTPException(404, "Book is not on your shelf")
    return row


@app.patch("/my-bookshelf/{provider_book_id}/set-favorite")
def update_favorite_status(provider_book_id: str, update: FavoriteUpdate, user_id: str = Depends(get_current_user_id), credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    entry = set_favorite_book(
            user_id=user_id,
            provider_book_id=provider_book_id,
            is_favorite=update.is_favorite,
            access_token=credentials.credentials

    )
    return entry

    # Share books with friends?
    # Share reading history with friends?
    # Share library with friends?


@app.post("/my-bookshelf/recommendations", response_model=BookSearchResult)
def mock_book_recommendations(limit: int = Query(25, ge=1, le=50), user_id: str = Depends(get_current_user_id)):
    return get_recommendation(user_id, limit)


