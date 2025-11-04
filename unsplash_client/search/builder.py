from typing import Self

from unsplash_client.search.models import (
    ContentFilter, 
    OrderBy, 
    Orientation, 
    UnsplashSearchParams
)

class UnsplashSearchParamsBuilder:
    def __init__(self) -> None:
        self._query = ""
        self._limit = 10
        self._orientation = Orientation.LANDSCAPE
        self._content_filter = ContentFilter.HIGH
        self._page = 1
        self._order_by = OrderBy.RELEVANT

    def wioth_query(self, query: str) -> Self:
        self._query = query
        return self
    
    def with_limit(self, count: int) -> Self:
        self._limit = count
        return self
    
    def with_orientation(self, orientation: Orientation) -> Self:
        self._orientation = orientation
        return self
    
    def with_landscape(self) -> Self:
        self._orientation = Orientation.LANDSCAPE
        return self
    
    def with_portrait(self) -> Self:
        self._orientation = Orientation.PORTRAIT
        return self
    
    def with_squarish(self) -> Self:
        self._orientation = Orientation.SQUARISH
        return self
    
    def with_content_filter(self, filter: ContentFilter) -> Self:
        self._content_filter = filter
        return self
    
    def with_high_quality(self) -> Self:
        self._content_filter = ContentFilter.HIGH
        return self
    
    def with_low_quality(self) -> Self:
        self._content_filter = ContentFilter.LOW
        return self
    
    def with_page(self, page_num: int) -> Self:
        self._page = page_num
        return self
    
    def with_order_by(self, order: OrderBy) -> Self:
        self._order_by = order
        return self
    
    def with_relevant(self) -> Self:
        self._order_by = OrderBy.RELEVANT
        return self
    
    def with_latest(self) -> Self:
        self._order_by = OrderBy.LATEST
        return self
    
    def build(self) -> UnsplashSearchParams:
        return UnsplashSearchParams(
            query=self._query,
            per_page=self._limit,
            orientation=self._orientation,
            content_filter=self._content_filter,
            page=self._page,
            order_by=self._order_by,
        )