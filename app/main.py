import json
from uuid import UUID
import httpx
from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas.book_model import AddToShelfRequest, AuthorInfo, BookInfo, BookSearchResult, Edition
from app.schemas.bookshelf_model import FavoriteUpdate, Status
from app.settings import settings
from app.schemas.auth_model import UserProfile
from app.schemas.hardcover_api_schema import author_query, title_query, search_query, isbn_query, to_slug
from app.dbs.supabase_db import get_bookshelf, set_book_status_in_bookshelf, set_favorite_book, user_sign_up, user_login, create_user_profile, get_current_user_id
# from app.services.embeddings.embeddings import get_book_embeddings
from app.temp.temp_data import favorites
import isbnlib 


origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
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
async def search_books(query: str, page: int = 1, per_page: int = 100) -> BookSearchResult:
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
    print(res)
    if isinstance(res, str):
        res = json.loads(res)

    return BookSearchResult(found=res["found"], hits=[BookInfo.model_validate(hit["document"]) for hit in res["hits"]], page=res["page"])


@app.get("/search/title/{book_title}", response_model=list[BookInfo])
async def get_book_by_title(book_title: str) -> list[BookInfo]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.hardcover_api_url, 
                json={"query": title_query , "variables": {"title": book_title}},
                headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"})
                
    except httpx.RequestError as e:

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Hardcover API is unavailable: {e}")
    

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail={e})
    data = response.json()
    print(data)
    res = [BookInfo(**b) for b in data["data"]["books"]]
    return res


@app.get("/search/author/{author_name}", response_model=AuthorInfo)
async def get_author_info(author_name: str):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.hardcover_api_url, 
                json={"query": author_query , "variables": {"slug": to_slug(author_name)}},
                headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"})
                
            if response.status_code == 200:
                data = response.json()
            return AuthorInfo(**data["data"]["authors"][0]) if data["data"]["authors"] else None
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Hardcover API is unavailable: {e}")


@app.get("/search/isbn/{isbn}")
async def get_book_info_by_isbn(isbn: str):
    field = ""
    isbn = isbnlib.canonical(isbn)

    if isbnlib.is_isbn10(isbn):
        field = "isbn_10"
    elif isbnlib.is_isbn13(isbn):
        field = "isbn_13"

    query = isbn_query.replace("FIELD", field)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.hardcover_api_url, 
                json={"query": query , "variables": {"isbn": isbn }},
                headers={ "Authorization": f"Bearer {settings.hardcover_api_key}", "content-type": "application/json"})
                
            data = response.json()

            if response.status_code == 200 and data:
                return [Edition(**b) for b in data["data"]["editions"]]

            return []
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Hardcover API is unavailable: {e}")


# @app.get("/books", response_model=BookResp)
# async def get_book_info_by_author(author_name: Optional[str] = Query(None, description="Search by author name"), book_title: Optional[str] = Query(None, description="Search by book title")):
#     url = f"https://openlibrary.org/search.json"

#     if not author_name and not book_title:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide a book title or author name"
#         )
    
#     params = {
#         "fields": "key,author_key,author_name,subject,first_sentence,cover_i",
#     } 
#     if author_name:
#         params["author"] = author_name

#     async with httpx.AsyncClient(timeout=5.0) as client:
#         try:
#             response = await client.get(url, params=params)
#             response.raise_for_status()

#         except httpx.RequestError:
#             raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Open library API is unavailable")

#     try:
#         data = {**response.json(), "docs": [Docs(**items) for items in response.json()["docs"]]}
#         resp = BookResp(**data)
#         return resp

#     except (ValueError, KeyError, TypeError) as e:
#         raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f'{str(e)}')



# async def enrich_book_details(book: Docs) -> Docs:
#     if book.key:
#         url = f"https://openlibrary.org{book.key}.json"

#         async with httpx.AsyncClient(timeout=5.0) as client:
#             response = await client.get(url)
#             response.raise_for_status()
#             work = WorkDetails(**response.json())
#             description = work.description.value if isinstance(work.description, WorkDescription) else work.description

#         return book.model_copy(update={"description": book.description or description, "subjects": book.subjects or work.subjects})


    
    
@app.post('/my-bookshelf/sign-up')
async def create_new_user(email: str, password: str):
    new_user = await user_sign_up(email, password)
    return new_user


@app.post('/my-bookshelf/login')
async def login_User(email: str, password: str):
    logged_in = await user_login(email, password)
    return logged_in


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
    
@app.post("/my-bookshelf/set-status")
def set_book_status(request: AddToShelfRequest, user_ID: str = Depends(get_current_user_id), credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return set_book_status_in_bookshelf(
        book=request.book,
        status=request.status,
        user_id=user_ID,
        access_token=credentials.credentials
    )


@app.get("/my-bookshelf")
def get_user_bookshelf(user_ID: str = Depends(get_current_user_id), credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return get_bookshelf(
        user_id=user_ID,
        access_token=credentials.credentials
    )

@app.patch("/my-bookshelf/{book_id}/favorite")
def update_favorite_status(book_id: UUID, update: FavoriteUpdate, user_id: str = Depends(get_current_user_id), credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    entry = set_favorite_book(
            user_id=user_id,
            book_id=book_id,
            is_favorite=update.is_favorite,
            access_token=credentials.credentials

    )

    return entry

    # Share books with friends?
    # Share reading history with friends?
    # Share library with friends?


    # Along with the search functionality, we need to implement a recommendation system that can suggest books based on user preferences and reading history. This will require us to store user data and book data in a database, and then use machine learning models to generate recommendations.
    # Need to find the best model for embedding the book data and the user preferences.

@app.post("/my-shelf/recommendations")
def mock_book_recommendations():
    for book in favorites:
        print(book.model_dump())

