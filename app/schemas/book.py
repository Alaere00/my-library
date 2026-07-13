from pydantic import BaseModel


class Book(BaseModel):
    id: str
    title: str
    subtitle: str | None = None 
    authors: list[str] = []
    description: str = ""
    categories: list[str] = []


class BookInfo(BaseModel): 
    page_count: int
    print_type: str
    categories: list[str] = []
    average_rating: float | None = None
    ratings_count: int | None = None
    maturity_rating: str | None = None
    publisher: str | None = None
    published_date: str | None = None



class SearchResult(BaseModel):
    query: str
    books: list[Book]


class RecommendationRequest(BaseModel):
    book_id: str


class RecommendationResponse(BaseModel):
    source: Book
    recommendations: list[Book]
