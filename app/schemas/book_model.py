from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, computed_field, field_validator

class Series(BaseModel):
    author: Optional[str] = None
    author_id: Optional[int] = None
    books_count: Optional[int] = None
    description: Optional[str] = None
    id: int
    is_completed: Optional[bool]
    locked: Optional[bool] = None
    name: str
    primary_books_count: int
    user_id: int 


class Book(BaseModel):
    book: str
    book_id: int 
    compilation: Optional[bool] = None
    created_at: Optional[str] = None
    details: Optional[str] = None
    featured: Optional[bool] = None
    id: int
    position: Optional[int] = None
    series: Optional[Series] = None
    series_id: Optional[int] = None
    updated_at: Optional[str] = None

class Character(BaseModel):
    name: str

class BookCharacter(BaseModel):
    character: Character


class CachedImage(BaseModel):
    id: Optional[int] = None
    url: Optional[str] = None
    color: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    color_name: Optional[str] = None


class BookInfo(BaseModel):
    title : Optional[str] = None 
    author_names: Optional[List[str]] = None
    book_characters: list[BookCharacter] = []
    content_warnings:  Optional[List[str]] = None
    cached_image: Optional[CachedImage] = None
    # contribution_types - Array of contribution types for contributions
    contributions: list[dict[str, Any]] = []
    description: Optional[str] = None
    featured_series: Optional[Series] = None
    featured_series_position: Optional[int] = None
    genres: Optional[List[str]] = None
    # isbns - The ISBNs of the book
    has_audiobook:  Optional[bool] = None
    has_ebook: Optional[bool] = None
    pages:  Optional[int] = None
    rating:  Optional[float] = None
    ratings_count:  Optional[int] = None
    release_date_i:  Optional[int] = None
    release_year: Optional[int] = None
    series_names: Optional[List[str]] = None
    subtitle: Optional[str] = None
    tags: Optional[List[str]] = None


class Contribution(BaseModel):
    book: BookInfo


class AuthorInfo(BaseModel):
    alternate_names: Optional[List[str]] = None
    bio: Optional[str] = None
    books_count: Optional[int] = None
    cached_image: Optional[CachedImage] = None
    contributions: list[Contribution]
    identifiers: Optional[Dict[str, list[str]]] = None
    image_id: Optional[int] = None
    is_bipoc: Optional[bool] = None
    name: str 


#########################################

class Docs(BaseModel):
    key: Optional[str] = None
    author_key: Optional[List[str]] = None
    author_name: Optional[List[str]] = None
    cover_edition_key: Optional[str] = None
    cover_i: Optional[int] = None
    ebook_acces: Optional[bool] = None
    edition_count: Optional[int] = None
    first_publish_year: Optional[int] = None
    has_fulltext:  Optional[bool] = None
    public_scan_b: Optional[bool] = None
    title: Optional[str] = None
    first_sentence: Optional[List[str]] = None
    description: Optional[List[str]] = None
    subjects: Optional[List[str]] = None

    @computed_field
    def cover_url(self) -> Optional[str]:
        if self.cover_i:
            return f'https://covers.openlibrary.org/b/id/{self.cover_i}-M.jpg'
        return None


class WorkDescription(BaseModel):
    type: Optional[str] = None
    value: Optional[str] = None


class WorkDetails(BaseModel):
    description: Optional[str | WorkDescription] = None
    subjects: Optional[List[str]] = None



class BookResp(BaseModel):
    numFound: int
    start: int
    numFoundExact: bool
    docs: List[Docs]


class FavoriteCreate(BaseModel):
    provider: Literal["openlibrary", "hardcover"]
    book: Docs