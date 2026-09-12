from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class IndustryIdentifiers(BaseModel):
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
    items: Optional[List[BookDetails]] = []



class RecommendationRequest(BaseModel):
    book_id: str


# class RecommendationResponse(BaseModel):
#     source: Book
#     recommendations: list[Book]

class ImageLinks(BaseModel):
    smallThumbnail: Optional[str] = None
    thumbnail: Optional[str] = None


class VolumeInfo(BaseModel):
    title: str
    authors: Optional[list[str]] = None
    publisher: Optional[str] = None
    publishedDate: Optional[str] = None
    description: Optional[str] = None
    # industryIdentifiers: Optional[List[IndustryIdentifiers]] = None
    industryIdentifiers: List[Dict[str, str]] = None
    pageCount: Optional[int] = None
    printType: Optional[str] = None
    mainCategory: Optional[str] = None
    averageRating: Optional[int] = None
    ratingsCount: Optional[int] = None
    imageLinks: Optional[ImageLinks] = None
    language: Optional[str] = None
    infoLink: Optional[str] = None

class ItemsResp(BaseModel):
    kind: str
    id: str
    etag: str
    selfLink: str
    volumeInfo: VolumeInfo


 
class TitleResponse(BaseModel):
    kind: str
    totalItems: int
    items: Optional[List[ItemsResp]] = None