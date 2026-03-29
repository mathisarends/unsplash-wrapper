from unsplash_wrapper.search.builder import UnsplashSearchParamsBuilder
from unsplash_wrapper.search.models import (
    ContentFilter,
    OrderBy,
    Orientation,
)


class TestUnsplashSearchParamsBuilderDefaults:
    def test_build_with_query_uses_defaults(self) -> None:
        params = UnsplashSearchParamsBuilder().query("mountains").build()
        assert params.query == "mountains"
        assert params.per_page == 10
        assert params.orientation == Orientation.LANDSCAPE
        assert params.content_filter == ContentFilter.HIGH
        assert params.page == 1
        assert params.order_by == OrderBy.RELEVANT


class TestUnsplashSearchParamsBuilderQuery:
    def test_query_sets_search_term(self) -> None:
        params = UnsplashSearchParamsBuilder().query("sunset").build()
        assert params.query == "sunset"


class TestUnsplashSearchParamsBuilderLimit:
    def test_limit_sets_per_page(self) -> None:
        params = UnsplashSearchParamsBuilder().query("cats").limit(5).build()
        assert params.per_page == 5


class TestUnsplashSearchParamsBuilderOrientation:
    def test_orientation_sets_value(self) -> None:
        params = (
            UnsplashSearchParamsBuilder()
            .query("dogs")
            .orientation(Orientation.PORTRAIT)
            .build()
        )
        assert params.orientation == Orientation.PORTRAIT

    def test_landscape_orientation_shortcut(self) -> None:
        params = (
            UnsplashSearchParamsBuilder()
            .query("dogs")
            .portrait_orientation()
            .landscape_orientation()
            .build()
        )
        assert params.orientation == Orientation.LANDSCAPE

    def test_portrait_orientation_shortcut(self) -> None:
        params = (
            UnsplashSearchParamsBuilder().query("dogs").portrait_orientation().build()
        )
        assert params.orientation == Orientation.PORTRAIT

    def test_squarish_orientation_shortcut(self) -> None:
        params = (
            UnsplashSearchParamsBuilder().query("dogs").squarish_orientation().build()
        )
        assert params.orientation == Orientation.SQUARISH


class TestUnsplashSearchParamsBuilderContentFilter:
    def test_content_filter_sets_value(self) -> None:
        params = (
            UnsplashSearchParamsBuilder()
            .query("nature")
            .content_filter(ContentFilter.LOW)
            .build()
        )
        assert params.content_filter == ContentFilter.LOW

    def test_high_quality_shortcut(self) -> None:
        params = (
            UnsplashSearchParamsBuilder()
            .query("nature")
            .low_quality()
            .high_quality()
            .build()
        )
        assert params.content_filter == ContentFilter.HIGH

    def test_low_quality_shortcut(self) -> None:
        params = UnsplashSearchParamsBuilder().query("nature").low_quality().build()
        assert params.content_filter == ContentFilter.LOW


class TestUnsplashSearchParamsBuilderPage:
    def test_page_sets_page_number(self) -> None:
        params = UnsplashSearchParamsBuilder().query("sky").page(3).build()
        assert params.page == 3


class TestUnsplashSearchParamsBuilderOrderBy:
    def test_order_by_sets_value(self) -> None:
        params = (
            UnsplashSearchParamsBuilder()
            .query("forest")
            .order_by(OrderBy.LATEST)
            .build()
        )
        assert params.order_by == OrderBy.LATEST

    def test_order_by_relevant_shortcut(self) -> None:
        params = (
            UnsplashSearchParamsBuilder()
            .query("forest")
            .order_by_latest()
            .order_by_relevant()
            .build()
        )
        assert params.order_by == OrderBy.RELEVANT

    def test_order_by_latest_shortcut(self) -> None:
        params = UnsplashSearchParamsBuilder().query("forest").order_by_latest().build()
        assert params.order_by == OrderBy.LATEST


class TestUnsplashSearchParamsBuilderChaining:
    def test_full_chain_builds_correct_params(self) -> None:
        params = (
            UnsplashSearchParamsBuilder()
            .query("ocean")
            .limit(20)
            .portrait_orientation()
            .low_quality()
            .page(2)
            .order_by_latest()
            .build()
        )
        assert params.query == "ocean"
        assert params.per_page == 20
        assert params.orientation == Orientation.PORTRAIT
        assert params.content_filter == ContentFilter.LOW
        assert params.page == 2
        assert params.order_by == OrderBy.LATEST

    def test_methods_return_self_for_chaining(self) -> None:
        builder = UnsplashSearchParamsBuilder()
        assert builder.query("test") is builder
        assert builder.limit(5) is builder
        assert builder.orientation(Orientation.LANDSCAPE) is builder
        assert builder.page(1) is builder
        assert builder.order_by(OrderBy.RELEVANT) is builder
        assert builder.landscape_orientation() is builder
        assert builder.portrait_orientation() is builder
        assert builder.squarish_orientation() is builder
        assert builder.high_quality() is builder
        assert builder.low_quality() is builder
        assert builder.order_by_relevant() is builder
        assert builder.order_by_latest() is builder
        assert builder.content_filter(ContentFilter.HIGH) is builder
