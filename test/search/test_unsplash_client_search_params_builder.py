import pytest

from unsplash_client.search.builder import UnsplashSearchParamsBuilder
from unsplash_client.search.models import ContentFilter, OrderBy, Orientation


def test_build_with_defaults():
    builder = UnsplashSearchParamsBuilder().wioth_query("test query")
    params = builder.build()
    assert params.query == "test query"
    assert params.per_page == 10
    assert params.orientation == Orientation.LANDSCAPE
    assert params.content_filter == ContentFilter.HIGH
    assert params.page == 1
    assert params.order_by == OrderBy.RELEVANT

def test_build_with_all_parameters():
    params = (
        UnsplashSearchParamsBuilder()
        .wioth_query("nature")
        .with_limit(20)
        .with_orientation(Orientation.PORTRAIT)
        .with_content_filter(ContentFilter.LOW)
        .with_page(3)
        .with_order_by(OrderBy.LATEST)
        .build()
    )
    assert params.query == "nature"
    assert params.per_page == 20
    assert params.orientation == Orientation.PORTRAIT
    assert params.content_filter == ContentFilter.LOW
    assert params.page == 3
    assert params.order_by == OrderBy.LATEST

def test_with_landscape_convenience_method():
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_landscape().build()
    assert params.orientation == Orientation.LANDSCAPE

def test_with_portrait_convenience_method():
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_portrait().build()
    assert params.orientation == Orientation.PORTRAIT

def test_with_squarish_convenience_method():
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_squarish().build()
    assert params.orientation == Orientation.SQUARISH

def test_with_high_quality_convenience_method():
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_high_quality().build()
    assert params.content_filter == ContentFilter.HIGH

def test_with_low_quality_convenience_method():
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_low_quality().build()
    assert params.content_filter == ContentFilter.LOW

def test_with_relevant_convenience_method():
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_relevant().build()
    assert params.order_by == OrderBy.RELEVANT

def test_with_latest_convenience_method():
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_latest().build()
    assert params.order_by == OrderBy.LATEST

def test_method_chaining_returns_self():
    builder = UnsplashSearchParamsBuilder().wioth_query("test")
    result = builder.with_limit(5)
    assert result is builder
    result = builder.with_landscape()
    assert result is builder
    result = builder.with_high_quality()
    assert result is builder

def test_overwrite_previous_values():
    params = (
        UnsplashSearchParamsBuilder()
        .wioth_query("test")
        .with_landscape()
        .with_portrait()
        .with_high_quality()
        .with_low_quality()
        .with_relevant()
        .with_latest()
        .build()
    )
    assert params.orientation == Orientation.PORTRAIT
    assert params.content_filter == ContentFilter.LOW
    assert params.order_by == OrderBy.LATEST

def test_multiple_builds_from_same_builder():
    builder = UnsplashSearchParamsBuilder().wioth_query("test").with_limit(15)
    params1 = builder.build()
    params2 = builder.build()
    assert params1.per_page == 15
    assert params2.per_page == 15
    assert params1 is not params2

def test_builder_state_after_build():
    builder = UnsplashSearchParamsBuilder().wioth_query("test").with_limit(20)
    params1 = builder.build()
    builder.with_limit(30)
    params2 = builder.build()
    assert params1.per_page == 20
    assert params2.per_page == 30

@pytest.mark.parametrize("per_page", [1, 10, 20, 30])
def test_with_different_per_page_values(per_page):
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_limit(per_page).build()
    assert params.per_page == per_page

@pytest.mark.parametrize("page", [1, 2, 5, 10, 100])
def test_with_different_page_values(page):
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_page(page).build()
    assert params.page == page

@pytest.mark.parametrize(
    "orientation,expected",
    [
        (Orientation.LANDSCAPE, Orientation.LANDSCAPE),
        (Orientation.PORTRAIT, Orientation.PORTRAIT),
        (Orientation.SQUARISH, Orientation.SQUARISH),
    ],
)
def test_with_orientation_enum_values(orientation, expected):
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_orientation(orientation).build()
    assert params.orientation == expected

@pytest.mark.parametrize(
    "content_filter,expected",
    [
        (ContentFilter.HIGH, ContentFilter.HIGH),
        (ContentFilter.LOW, ContentFilter.LOW),
    ],
)
def test_with_content_filter_enum_values(content_filter, expected):
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_content_filter(content_filter).build()
    assert params.content_filter == expected

@pytest.mark.parametrize(
    "order_by,expected",
    [
        (OrderBy.RELEVANT, OrderBy.RELEVANT),
        (OrderBy.LATEST, OrderBy.LATEST),
    ],
)
def test_with_order_by_enum_values(order_by, expected):
    params = UnsplashSearchParamsBuilder().wioth_query("test").with_order_by(order_by).build()
    assert params.order_by == expected

def test_complex_realistic_scenario():
    params = (
        UnsplashSearchParamsBuilder()
        .wioth_query("sunset beach")
        .with_limit(25)
        .with_landscape()
        .with_high_quality()
        .with_latest()
        .with_page(2)
        .build()
    )
    assert params.query == "sunset beach"
    assert params.per_page == 25
    assert params.orientation == Orientation.LANDSCAPE
    assert params.content_filter == ContentFilter.HIGH
    assert params.order_by == OrderBy.LATEST
    assert params.page == 2

def test_query_is_preserved_through_chaining():
    query = "architecture photography"
    params = (
        UnsplashSearchParamsBuilder()
        .wioth_query(query)
        .with_limit(15)
        .with_squarish()
        .build()
    )
    assert params.query == query