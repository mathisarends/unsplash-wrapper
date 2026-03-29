from typing import Self

from unsplash_wrapper.search.models import (
    ContentFilter,
    OrderBy,
    Orientation,
    UnsplashSearchParams,
)


class UnsplashSearchParamsBuilder:
    def __init__(self) -> None:
        self._query = ""
        self._limit = 10
        self._orientation = Orientation.LANDSCAPE
        self._content_filter = ContentFilter.HIGH
        self._page = 1
        self._order_by = OrderBy.RELEVANT
        self._total_results_limit: int | None = None

    def query(self, query: str) -> Self:
        self._query = query
        return self

    def limit(self, count: int) -> Self:
        self._limit = count
        return self

    def orientation(self, orientation: Orientation) -> Self:
        self._orientation = orientation
        return self

    def landscape_orientation(self) -> Self:
        self._orientation = Orientation.LANDSCAPE
        return self

    def portrait_orientation(self) -> Self:
        self._orientation = Orientation.PORTRAIT
        return self

    def squarish_orientation(self) -> Self:
        self._orientation = Orientation.SQUARISH
        return self

    def content_filter(self, filter: ContentFilter) -> Self:
        self._content_filter = filter
        return self

    def high_quality(self) -> Self:
        self._content_filter = ContentFilter.HIGH
        return self

    def low_quality(self) -> Self:
        self._content_filter = ContentFilter.LOW
        return self

    def page(self, page_num: int) -> Self:
        self._page = page_num
        return self

    def order_by(self, order: OrderBy) -> Self:
        self._order_by = order
        return self

    def order_by_relevant(self) -> Self:
        self._order_by = OrderBy.RELEVANT
        return self

    def order_by_latest(self) -> Self:
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
            total_results_limit=self._total_results_limit,
        )
