from typing import List
import httpx
from app.schemas.book_model import TitleResponse, VolumeInfo, AuthorResp, Docs
from fastapi import FastAPI, HTTPException, Depends, Header
import requests
from app.settings import settings
from app.schemas.auth_model import UserProfile
from fastapi.middleware.cors import CORSMiddleware
from app.dbs.supabase_db import user_sign_up, create_user_profile, get_current_user_id
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


@app.get("/healthz")
def read_root():
    return {"message": "Hello World"}

@app.get("/search")
async def universal_search(q: str, page: int = 1, per_page: int = 10):
    validated_isbn = isbnlib.canonical(q)
 
    if validated_isbn:
        return get_book_info_by_isbn(q)
    else: 
        title_details = await get_title_by_name_or_author(q, page, per_page)

    return title_details

# title or author -> universal search
async def get_title_by_name_or_author(query: str, page: int = 1, per_page: int = 10):
    max_results = min(per_page,  40)

    start_index = (page - 1) * max_results

    params = {
        "q": f':"{query}"+OR+inauthor:"{query}"',
        "key": settings.google_books_api_key,
        "printType": "books",
        "projection": "full",
        "startIndex": start_index,
        "maxResults": per_page

    }

    url = settings.google_books_api_url
 
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = TitleResponse(**resp.json())


    if not data:
        return []
    else:
        return data


@app.get("/search/{isbn}/info")
def get_book_info_by_isbn(isbn: str, page: int = 1, limit: int = 10) -> List[VolumeInfo]:
    max_results = min(limit, 40)
    start_index = (page - 1) * max_results
    params = {"key": settings.google_books_api_key, "startIndex": start_index, "maxResult": max_results}
    try: 
        response = requests.get(f"{settings.google_books_api_url}?q=isbn:{isbn}", params=params)
        response.status_code()
        data = TitleResponse(**response.json())

        volume_info = [info.volumeInfo for info in data.items]
    except requests.ConnectionError as e:
        print("Connection error", e.response)

    return volume_info

@app.get("/search/title-info")
def get_book_info_by_title(query: str):
    pass



@app.get("/search/by-author/{author_name}")
def get_book_info_by_author(author_name: str):
    url = f"https://openlibrary.org/search.json?author={author_name}"
    response = requests.get(url=url, timeout=5)
    response.raise_for_status()

    if response.ok:
        try:
            data = {**response.json(), "docs": [Docs(**items) for items in response.json()["docs"]]}

            author_resp = AuthorResp(**data)

        except ValueError as e:
            print("Response error", response.text)


    return author_resp

    

@app.post('/sign_up/{email}/{password}')
async def create_new_user(email: str, password: str):
    new_user = await user_sign_up(email, password)

    return new_user

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


@app.post("/my-shelf/favorite/{title}")
def add_title_to_favorites(title: str):
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

