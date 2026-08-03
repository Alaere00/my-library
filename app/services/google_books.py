from app.schemas.book_model import Book, BookInfo, BookResponse
from rapidfuzz import fuzz
import re


def parse_volume(item: dict) -> Book:
    info = item.get("volumeInfo", {})
    print(info)
    return Book(
        id=item["id"],
        title=info.get("title", "Unknown"),
        authors=info.get("authors", []),
        description=info.get("description", ""),
        categories=info.get("categories", []),
        subtitle=info.get("subtitle"),
        images=info.get("imageLinks", {}),
        # industryIdentifiers=info.get("industryIndentifiers", [{}])
    )


def get_book_info(item: dict) -> BookInfo:
    info = item.get("volumeInfo", {})
    return BookInfo(
        page_count=info.get("pageCount", 0),
        print_type=info.get("printType", ""),
        categories=info.get("categories", []),
        average_rating=info.get("averageRating"),
        ratings_count=info.get("ratingsCount"),
        maturity_rating=info.get("maturityRating"),
        publisher=info.get("publisher"),
        published_date=info.get("publishedDate"),
    )


def get_books_by_isbn(response: BookResponse, isbn: str):
    book_details = []

    for book_info in response:
        for book in book_info['volumeInfo']['industryIdentifiers']:
            print(book)
            if book['identifier'] == isbn:
                book_details.append(book_info['volumeInfo'])

    return book_details


def get_books_by_author(response: BookResponse, author_name: str):
    book_details = []
    author_name = normalize(author_name.strip())

    for book in response:
        for author in book['volumeInfo']['authors']:
            ratio = fuzz.ratio(author_name, normalize(author))
            if ratio > 50:
                book_details.append(book)

    # need to map out the details I actually want to store, but this works for now 

    return book_details


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()
