from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class IndustryIdentifier(BaseModel):
    type: str
    identifier: str

class BookDetails(BaseModel): 
    id: Optional[str] = None
    kind: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    authors: Optional[list[str]] = []
    description: Optional[str] = None
    categories: Optional[list[str]] = None
    pageCount: Optional[int] = None
    printType: Optional[str] = None
    # averageRating: Optional[float] = None
    # ratingsCount: Optional[int] = None
    maturityRating: Optional[str] = None
    imageLinks: Optional[Any] = None
    publisher: Optional[str] = None
    publishedDate: Optional[str] = None
    industryIdentifiers: List[Dict[str, str]] = None


class BookResponse(BaseModel):
    totalItems: Optional[int] = None
    # id: Optional[str] = None
    items: Optional[List[BookDetails]] = []



# class SearchResult(BaseModel):
#     query: str
#     books: list[Book]


class RecommendationRequest(BaseModel):
    book_id: str


# class RecommendationResponse(BaseModel):
#     source: Book
#     recommendations: list[Book]


class Docs(BaseModel):
    author_key: list[str]
    author_name: list[str]
    cover_edition_key: Optional[str] = None
    cover_i: Optional[int] = None
    edition_count: int
    first_publish_year: int
    has_full_text: Optional[bool] = None
    key: str
    language: Optional[list[str]] = None
    title: str


class Author(BaseModel):
    numFound: int
    numFoundExact: Optional[bool]
    num_found: int
    offset: Optional[int] = None
    docs: list[Docs]

