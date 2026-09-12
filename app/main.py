import http
import httpx
from app.schemas.book_model import TitleResponse
from fastapi import FastAPI, HTTPException, Depends, Header
import requests
from app.settings import settings
from app.services.google_books import get_books_by_isbn
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

params = {"key": settings.google_books_api_key}

@app.get("/healthz")
def read_root():
    return {"message": "Hello World"}

@app.get("/search")
async def universal_search(query: str):
    validated_isbn = isbnlib.canonical(query)
 
    if validated_isbn:
        return get_book_info_by_isbn(query)
    else: 
        title_details = await get_title_by_name_or_author(query)

    return title_details

# title or author -> combined into one for simplicity 
async def get_title_by_name_or_author(query: str):
    url = settings.google_books_api_url
    q_params = {"q": f':"{query}"+OR+inauthor:"{query}"', "key": params["key"], "orderBy": "relevance",   }
  
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=q_params)
        data = TitleResponse(**resp.json())


    if not data:
        return []
    else:
        return data

    
# @app.get("/book/{isbn}/info")
def get_book_info_by_isbn(isbn: str):
    response = requests.get(f"{settings.google_books_api_url}?q=isbn:{isbn}", params=params)
    data = response.json()

    book_by_isbn = get_books_by_isbn(data.get('items', []), isbn)

    return book_by_isbn


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

