from app.schemas.book_model import BookInfo


def to_book_info(b: dict, fallback_authors: str = None) -> BookInfo:
    tags = b.get("cached_tags") or {}

    def names(category: str) -> list[str]:
        return [t["tag"] for t in tags.get(category, []) if t.get("tag")]
    
    contributors = b.get("contributions") or []

    author_names = [
        c["author"]["name"] for c in contributors if c.get("author")
    ] or (fallback_authors or [])

    return BookInfo(
        id=b["id"],
        title=b.get("title"),
        subtitle=b.get("subtitle"),
        description=b.get("description"),
        image=b.get("cached_image"),
        genres=names("Genre"),
        moods=names("Mood"),
        content_warnings=names("Content Warning"),
        tags=names("Tag"),
        author_names=author_names,
        pages=b.get("pages"),
        release_year=b.get("release_year"),
        rating=b.get("rating"),
    )


def book_to_row(b: BookInfo) -> dict:

    return {
        "provider": "hardcover",
        "provider_book_id": str(b.id),
        "title": b.title,
        "subtitle": b.subtitle,
        "authors": b.author_names or [],
        "description": b.description,
        "genres": b.genres or [],
        "moods": b.moods or [],
        "tags": b.tags or [],
        "content_warnings": b.content_warnings or [],
        "series_names": b.series_names or [],
        "image": b.image.model_dump(exclude_none=True) if b.image else None,
        "pages": b.pages,
        "release_year": b.release_year,
        "rating": b.rating,
        "ratings_count": b.ratings_count,
    }