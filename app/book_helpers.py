from app.schemas.book_model import BookInfo


def to_book_info(b: dict) -> BookInfo:
    tags = b.get("cached_tags") or {}

    def names(category: str) -> list[str]:
        return [t["tag"] for t in tags.get(category, []) if t.get("tag")]
    
    print(b.get("contributions") )
    contributors = b.get("contributions") or []

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
        author_names=[
            c["author"]["name"] for c in contributors if c.get("author")],
        pages=b.get("pages"),
        release_year=b.get("release_year"),
        rating=b.get("rating"),
    )