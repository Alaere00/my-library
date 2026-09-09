import http
import httpx
from app.schemas.book_model import BookResponse, Author
from fastapi import FastAPI, HTTPException
import requests
from app.settings import settings
from app.services.google_books import get_title_details, get_books_by_isbn, get_titles_by_author
from fastapi.middleware.cors import CORSMiddleware
from app.dbs.supabase_db import user_sign_up
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

@app.get("/search", response_model=list[Author| BookResponse])
async def universal_search(query: str):
    combined_results: list[Author | BookResponse] = []

    validated_isbn = isbnlib.canonical(query)
 
    if validated_isbn:
        return get_book_info_by_isbn(query)
    

    title_by_author = await list_books_by_author(query)
    title_details = await get_title(query)

        # combined_results.append(title_by_author)
        # combined_results.append(title_details)

# <class 'app.schemas.book_model.Author'>
# <class 'app.schemas.book_model.BookResponse'>


    return combined_results


# @app.get("/book/{title}")
async def get_title(title: str):
    response = requests.get(f"{settings.google_books_api_url}?q=intitle:{title}", params={ "key": settings.google_books_api_key})
    if response.status_code == http.HTTPStatus.OK:
        data = response.json()

        title_details = get_title_details(data)
        return title_details

    raise HTTPException(status_code=response.status_code, detail="Failed to fetch book data")
    


# @app.get("/author/{author_name}")
async def list_books_by_author(author_name: str) -> Author:
    url = f"https://openlibrary.org/search.json?author={author_name}&fields=title"

    headers = {
        "User-Agent": settings.user_agent
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        data = resp.json()

    author_titles = get_titles_by_author(data)
    
    return author_titles



@app.get("/book/{isbn}/info")
def get_book_info_by_isbn(isbn: str):
    params = {
    "key": settings.google_books_api_key
}
    response = requests.get(f"{settings.google_books_api_url}?q=isbn:{isbn}", params=params)
    data = response.json()

    book_by_isbn = get_books_by_isbn(data.get('items', []), isbn)

    return book_by_isbn


@app.post('/sign_up/{email}/{password}')
async def create_new_user(email: str, password: str):
    new_user = await user_sign_up(email, password)

    return new_user


@app.post("/my-shelf/{book_name}")
def save_book_by_title(book_name):
    pass
    # API Endpoints:
    # Search books by title, author, or category -> needs to be in a separate file related to the search functionality
    # 1 get book by title (done)
    # 2 get book info by isbn (done)
    # 3 get book by Author (done)


    # Personal Library Endpoints:
    # My bookshelf 
    # Favotrite books
    # Read this year
    # To be read

    # Add books to personal library
    # Remove books from personal library
    # Mark favorites 

    # Share books with friends?
    # Share reading history with friends?
    # Share library with friends?


    # Along with the search functionality, we need to implement a recommendation system that can suggest books based on user preferences and reading history. This will require us to store user data and book data in a database, and then use machine learning models to generate recommendations.
    # Need to find the best model for embedding the book data and the user preferences.

