from app.schemas.book_model import BookDetails, BookResponse, Author, Docs


def get_title_details(api_resp: dict) -> BookResponse:
    book_list = api_resp.get("items", [])

    parsed_books = []

    for book_detail in book_list:
        volume = book_detail["volumeInfo"]
        details = BookDetails(
                kind=book_detail.get("kind"),
                id=book_detail.get("id"),
                **volume
        )
        parsed_books.append(details)

    return BookResponse(
        totalItems=api_resp.get("totalItems", 0),
        items=parsed_books
    )


# need an ISBN parser & an exact match =
def get_books_by_isbn(api_response: BookResponse, isbn: str):
    book_details = []

    for book_info in api_response:
        for book in book_info['volumeInfo']['industryIdentifiers']:
            print(book)
 
            if book['identifier'] == isbn:
                book_details.append(book_info['volumeInfo'])

    return book_details

# def isbn_validator(isbn: str):

#     if len(isbn.strip('-')) != 10 or len(isbn.strip('-')):
#         return False

#     return 


def get_titles_by_author(item) -> Author:
    return Author(
        numFound=item.get("numFound", 0),
        numFoundExact=item.get('numFoundExact'),
        num_found=item.get('num_found', 0),
        offset=item.get("offset", 0),
        docs=[Docs(**docs) for docs in item.get('docs', [])]
    )



# fetching covers https://covers.openlibrary.org/a/olid/OL23919A-M.jpg