from app.schemas.book import Book, BookInfo


def parse_volume(item: dict) -> Book:
    info = item.get("volumeInfo", {})
    return Book(
        id=item["id"],
        title=info.get("title", "Unknown"),
        authors=info.get("authors", []),
        description=info.get("description", ""),
        categories=info.get("categories", []),
        subtitle=info.get("subtitle"),
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

