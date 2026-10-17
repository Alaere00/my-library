import json
import httpx
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header, Query, status
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.book_model import AuthorInfo, BookInfo, BookResp, BookSearchResult, Docs, WorkDetails, WorkDescription
from app.settings import settings
from app.schemas.auth_model import UserProfile
from app.schemas.hardcover_api_schema import author_query, title_query, search_query, to_slug
from app.dbs.supabase_db import user_sign_up, user_sign_in, create_user_profile, get_current_user_id
# from app.services.embeddings.embeddings import get_book_embeddings
import isbnlib 
from app.temp.temp_data import favorites


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


@app.get("/healthz")
def read_root():
    return {"message": "Hello World"}

@app.get("/general-search", response_model=BookSearchResult)
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


# @app.get("/books/{isbn}")
# def get_book_info_by_isbn(isbn: str, page: int = 1, limit: int = 10) -> List[VolumeInfo]:
#     max_results = min(limit, 40)
#     start_index = (page - 1) * max_results
#     params = {"key": settings.google_books_api_key, "startIndex": start_index, "maxResult": max_results}
#     try: 
#         response = requests.get(f"{settings.google_books_api_url}?q=isbn:{isbn}", params=params)
#         response.status_code()
#         data = TitleResponse(**response.json())

#         volume_info = [info.volumeInfo for info in data.items]
#     except requests.ConnectionError as e:
#         print("Connection error", e.response)

#     return volume_info


@app.get("/books", response_model=BookResp)
async def get_book_info_by_author(author_name: Optional[str] = Query(None, description="Search by author name"), book_title: Optional[str] = Query(None, description="Search by book title")):
    url = f"https://openlibrary.org/search.json"

    if not author_name and not book_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide a book title or author name"
        )
    
    params = {
        "fields": "key,author_key,author_name,subject,first_sentence,cover_i",
    } 
    if author_name:
        params["author"] = author_name

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Open library API is unavailable")

    try:
        data = {**response.json(), "docs": [Docs(**items) for items in response.json()["docs"]]}
        resp = BookResp(**data)
        return resp

    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f'{str(e)}')



async def enrich_book_details(book: Docs) -> Docs:
    if book.key:
        url = f"https://openlibrary.org{book.key}.json"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            work = WorkDetails(**response.json())
            description = work.description.value if isinstance(work.description, WorkDescription) else work.description

        return book.model_copy(update={"description": book.description or description, "subjects": book.subjects or work.subjects})



# @app.post("/books/embeddings")
# # method to test the embeddings for the books in the database
# def generate_book_embeddings():
#     return get_book_embeddings()

    
    
@app.post('/sign_up')
async def create_new_user(email: str, password: str):
    new_user = await user_sign_up(email, password)

    return new_user


@app.get('/sign_in')
async def sign_in_User(email: str, password: str):
    user_sign_in = await user_sign_in(email, password)
    return user_sign_in


@app.post('/update_profiles')
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
    

@app.post("/my_shelf/completed/{title}")
def add_read_title_to_shelf(title: str):
    pass



@app.post("/my-shelf/tbr/{title}")
def add_title_to_tbr(title):
    pass


@app.delete("my-shelf/TEMP/{title}")
def remove_title_from_shelf(shelf_type, title):
    pass
    # in the database correlate the shelf type and remove the title 

    # database for bookshelf 



    # Share books with friends?
    # Share reading history with friends?
    # Share library with friends?


    # Along with the search functionality, we need to implement a recommendation system that can suggest books based on user preferences and reading history. This will require us to store user data and book data in a database, and then use machine learning models to generate recommendations.
    # Need to find the best model for embedding the book data and the user preferences.

@app.post("/my-shelf/recommendations")
def mock_book_recommendations():
    for book in favorites:
        print(book.model_dump())

