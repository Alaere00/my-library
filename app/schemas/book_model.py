from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class IndustryIdentifier(BaseModel):
    type: str
    identifier: str

# class Docs(BaseModel):
#     author_key: list[str] = ""
#     author_name: list[str] = ""
#     cover_edition_key: Optional[str] = None
#     cover_i: Optional[int] = None
#     edition_count: int = None
#     first_publish_year: int = None
#     has_full_text: Optional[bool] = None
#     key: Optional[str] = None
#     language: Optional[list[str]] = None
#     title: str

class Docs(BaseModel):
    title: str
    author_key: list[str] = []
    author_name: list[str] = []
    edition_count: int = None
    first_publish_year: str = None


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

class Author(BaseModel):
    numFound: int
    numFoundExact: Optional[bool]
    offset: Optional[int] = None
    docs: list[Docs]

class BookResponse(BaseModel):
    totalItems: Optional[int] = None
    items: Optional[List[BookDetails]] = []



class RecommendationRequest(BaseModel):
    book_id: str


# class RecommendationResponse(BaseModel):
#     source: Book
#     recommendations: list[Book]





