from dataclasses import field
from typing import List, Dict
from pydantic import BaseModel


class IndustryIdentifier(BaseModel):
    type: str
    identifier: str


class Book(BaseModel):
    id: str
    title: str
    subtitle: str | None = None 
    authors: list[str] = []
    description: str = ""
    categories: list[str] = []

    # industryIdentifiers: list[IndustryIdentifier] = field(default_factory=list)



class AuthorBooks(BaseModel):
    title: str


class BookInfo(BaseModel): 
    page_count: int
    print_type: str
    categories: list[str] = []
    average_rating: float | None = None
    ratings_count: int | None = None
    maturity_rating: str | None = None
    publisher: str | None = None
    published_date: str | None = None

class BookDetails(BaseModel):
    title: str
    subtitle: str
    author: List[str]
    publisher: str
    publishedDate: str
    description: str
    industryIdentifiers: List[Dict[str, str]]
    pageCount: int
    categories: List[str]
    maturityRating: str
    imageLinks: str



class BookResponse(BaseModel):
    kind: str
    totalItems: int
    items: List[BookDetails]





class SearchResult(BaseModel):
    query: str
    books: list[Book]


class RecommendationRequest(BaseModel):
    book_id: str


class RecommendationResponse(BaseModel):
    source: Book
    recommendations: list[Book]
