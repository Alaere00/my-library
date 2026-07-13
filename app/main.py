import http
from typing import Union
from app.schemas.book import Book, BookInfo
from fastapi import FastAPI, HTTPException
import requests
from app.config import settings
from app.services.google_books import parse_volume


# MVP
# store books in some sort of database -> google firebase/firestore (I believe it's free)
# create a search endpoint
# search logic that queries the database for books matching the search term
# be able to give recommendations based off of user preferences 
# share personal library with others 
# generate recommendation from user reading history 
app = FastAPI()

Google_BOOKS_API_URL = "https://www.googleapis.com"

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/search")
def search_books(query: str):
    # Implement your search logic here
    # result = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}&key={settings.google_books_api_key}")
    
    return {"message": f"Searching books for query: {query}"}



# @app.get("/book/{book_id}", response_model=Union[Book, BookInfo])
# async def get_book_data():
#     response = requests.get(f"{Google_BOOKS_API_URL}/books/v1/volumes/{book_id}?key={settings.google_books_api_key}")

@app.get("/book/{book_title}", response_model=list[Book] | None)
def get_book_by_title(book_title: str):
    response = requests.get(f"{Google_BOOKS_API_URL}/books/v1/volumes?q={book_title}&key={settings.google_books_api_key}")

    if response.status_code == http.HTTPStatus.OK:
        data = response.json()
        books = [parse_volume(item) for item in data.get("items", [])]
        return books

    raise HTTPException(status_code=response.status_code, detail="Failed to fetch book data")
    



@app.get("/book/{author_name}", response_model=list[Book] | None)
def list_books_by_author(author_name: str):
    # response = requests.get(f"https://openlibrary.org/search/authors.json?q={author_name}")

    for author in response.json().get("docs", []):
        author_key = author.get("key")
        if author_key:
            works_response = requests.get(f"https://openlibrary.org{author_key}/works.json")
            if works_response.status_code == http.HTTPStatus.OK:
                works_data = works_response.json()
                books = []
                for work in works_data.get("entries", []):
                    book = {
                        "title": work.get("title"),
                    }
                    books.append(book)
                return books

    # return response.json()


app.get("/book/{book_id}/info", response_model=BookInfo | None)
def get_book_info_by_id(book_id: str):
    pass

    # API Endpoints:
    # Search books by title, author, or category -> needs to be in a separate file related to the search functionality
    # 1 get book by title
    # 3 get book info by id
    # 4 get book by Author


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