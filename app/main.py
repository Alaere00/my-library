import http
from app.schemas.book_model import Book, BookInfo, BookDetails
from fastapi import FastAPI, HTTPException
import requests
from app.config import settings
from app.services.google_books import parse_volume, get_books_by_isbn, get_books_by_author

# MVP
# store books in some sort of database -> google firebase/firestore (I believe it's free)
# create a search endpoint
# search logic that queries the database for books matching the search term
# be able to give recommendations based off of user preferences 
# share personal library with others 
# generate recommendation from user reading history 
app = FastAPI()

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"


@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/search")
def search_books(query: str):
    pass
    

@app.get("/book/{book_title}", response_model=list[Book] | None)
def get_book_by_title(book_title: str):
    response = requests.get(f"{GOOGLE_BOOKS_API_URL}?q={book_title}", params={ "key": settings.google_books_api_key})

    if response.status_code == http.HTTPStatus.OK:
        data = response.json()
        books = [parse_volume(item) for item in data.get("items", [])]
        return books

    raise HTTPException(status_code=response.status_code, detail="Failed to fetch book data")
    


@app.get("/book/author/{author_name}")
# title, publication, book cover, format/edition 
def list_books_by_author(author_name: str):
    params = {
        "q": f"inauthor:{author_name}",
        "key": settings.google_books_api_key
    }

    response = requests.get(f"{GOOGLE_BOOKS_API_URL}", params=params).json()

    author_books = get_books_by_author(response.get('items'), author_name)

    return author_books


@app.get("/book/{isbn}/info")
def get_book_info_by_id(isbn: str):
    params = {
    "key": settings.google_books_api_key
}
    response = requests.get(f"{GOOGLE_BOOKS_API_URL}?q=isbn: {isbn}&country=US", params=params)
    data = response.json()

    book_by_isbn = get_books_by_isbn(data.get('items', {}), isbn)

    return book_by_isbn





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


# api for book covers https://covers.openlibrary.org/b/$key/$value-$size.jpg