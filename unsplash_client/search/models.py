from enum import StrEnum
from pydantic import BaseModel, Field, HttpUrl


class Orientation(StrEnum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARISH = "squarish"


class ContentFilter(StrEnum):
    LOW = "low"
    HIGH = "high"


class OrderBy(StrEnum):
    RELEVANT = "relevant"
    LATEST = "latest"


class UnsplashUrls(BaseModel):
    raw: HttpUrl
    full: HttpUrl
    regular: HttpUrl
    small: HttpUrl
    thumb: HttpUrl


class UnsplashUser(BaseModel):
    id: str
    username: str
    name: str
    portfolio_url: HttpUrl | None = None
    bio: str | None = None
    location: str | None = None


class UnsplashPhoto(BaseModel):
    id: str
    description: str | None = None
    alt_description: str | None = "No description"
    urls: UnsplashUrls
    user: UnsplashUser
    width: int
    height: int
    color: str | None = None
    likes: int = 0
    created_at: str
    
    @property
    def url_regular(self) -> str:
        return str(self.urls.regular)


class UnsplashSearchParams(BaseModel):
    query: str
    per_page: int = 10
    orientation: Orientation = Orientation.LANDSCAPE
    content_filter: ContentFilter = ContentFilter.HIGH
    page: int = 1
    order_by: OrderBy = OrderBy.RELEVANT


class UnsplashSearchResponse(BaseModel):
    total: int
    total_pages: int
    results: list[UnsplashPhoto] = Field(default_factory=list)