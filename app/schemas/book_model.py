from typing import List, Dict, Optional, Any
from pydantic import BaseModel, computed_field


class IndustryIdentifiers(BaseModel):
    type: str
    identifier: str


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
    averageRating: Optional[int | float] = None
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

    @computed_field
    def cover_url(self) -> Optional[str]:
        if self.cover_i:
            return f'https://covers.openlibrary.org/b/id/{self.cover_i}-M.jpg'
        return None



# class Author(BaseModel):
    # text: Optional[list[str]] = None
    # type: Optional[str] = None
    # alternate_names: Optional[list[str]] = None
    # birth_date: Optional[str] = None
    # top_work: Optional[str] = None
    # work_count: Optional[int] = None
    # top_subjects: Optional[list[str]] = None
    # _version_: Optional[int] = None


class BookResp(BaseModel):
    numFound: int
    start: int
    numFoundExact: bool
    docs: List[Docs]
