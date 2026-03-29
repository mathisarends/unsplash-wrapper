import pytest
from pydantic import ValidationError

from unsplash_wrapper.search.models import (
    ContentFilter,
    OrderBy,
    Orientation,
    UnsplashPhoto,
    UnsplashSearchParams,
    UnsplashSearchResponse,
    UnsplashUrls,
    UnsplashUser,
)

VALID_URL = "https://images.unsplash.com/photo-1"


def _make_urls() -> dict:
    return {
        "raw": VALID_URL,
        "full": VALID_URL,
        "regular": VALID_URL,
        "small": VALID_URL,
        "thumb": VALID_URL,
    }


def _make_user() -> dict:
    return {
        "id": "user-1",
        "username": "testuser",
        "name": "Test User",
    }


def _make_photo(**overrides: object) -> dict:
    base = {
        "id": "photo-1",
        "description": "A test photo",
        "alt_description": "alt text",
        "urls": _make_urls(),
        "user": _make_user(),
        "width": 1920,
        "height": 1080,
        "color": "#ffffff",
        "likes": 42,
        "created_at": "2025-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


class TestOrientation:
    def test_landscape_value(self) -> None:
        assert Orientation.LANDSCAPE == "landscape"

    def test_portrait_value(self) -> None:
        assert Orientation.PORTRAIT == "portrait"

    def test_squarish_value(self) -> None:
        assert Orientation.SQUARISH == "squarish"


class TestContentFilter:
    def test_low_value(self) -> None:
        assert ContentFilter.LOW == "low"

    def test_high_value(self) -> None:
        assert ContentFilter.HIGH == "high"


class TestOrderBy:
    def test_relevant_value(self) -> None:
        assert OrderBy.RELEVANT == "relevant"

    def test_latest_value(self) -> None:
        assert OrderBy.LATEST == "latest"


class TestUnsplashUrls:
    def test_valid_urls(self) -> None:
        urls = UnsplashUrls(**_make_urls())
        assert VALID_URL in str(urls.regular)

    def test_invalid_url_raises_validation_error(self) -> None:
        data = _make_urls()
        data["raw"] = "not-a-url"
        with pytest.raises(ValidationError):
            UnsplashUrls(**data)


class TestUnsplashUser:
    def test_required_fields(self) -> None:
        user = UnsplashUser(**_make_user())
        assert user.id == "user-1"
        assert user.username == "testuser"
        assert user.name == "Test User"

    def test_optional_fields_default_to_none(self) -> None:
        user = UnsplashUser(**_make_user())
        assert user.portfolio_url is None
        assert user.bio is None
        assert user.location is None

    def test_optional_fields_with_values(self) -> None:
        data = _make_user()
        data["bio"] = "A bio"
        data["location"] = "Berlin"
        data["portfolio_url"] = "https://example.com"
        user = UnsplashUser(**data)
        assert user.bio == "A bio"
        assert user.location == "Berlin"


class TestUnsplashPhoto:
    def test_from_valid_data(self) -> None:
        photo = UnsplashPhoto(**_make_photo())
        assert photo.id == "photo-1"
        assert photo.width == 1920
        assert photo.height == 1080
        assert photo.likes == 42

    def test_url_property_returns_regular_url(self) -> None:
        photo = UnsplashPhoto(**_make_photo())
        assert VALID_URL in photo.url

    def test_default_alt_description(self) -> None:
        data = _make_photo()
        del data["alt_description"]
        photo = UnsplashPhoto(**data)
        assert photo.alt_description == "No description"

    def test_likes_default_to_zero(self) -> None:
        data = _make_photo()
        del data["likes"]
        photo = UnsplashPhoto(**data)
        assert photo.likes == 0

    def test_missing_required_field_raises_error(self) -> None:
        data = _make_photo()
        del data["id"]
        with pytest.raises(ValidationError):
            UnsplashPhoto(**data)


class TestUnsplashSearchParams:
    def test_defaults(self) -> None:
        params = UnsplashSearchParams(query="mountains")
        assert params.per_page == 10
        assert params.orientation == Orientation.LANDSCAPE
        assert params.content_filter == ContentFilter.HIGH
        assert params.page == 1
        assert params.order_by == OrderBy.RELEVANT

    def test_custom_values(self) -> None:
        params = UnsplashSearchParams(
            query="cats",
            per_page=5,
            orientation=Orientation.PORTRAIT,
            content_filter=ContentFilter.LOW,
            page=3,
            order_by=OrderBy.LATEST,
        )
        assert params.query == "cats"
        assert params.per_page == 5
        assert params.orientation == Orientation.PORTRAIT
        assert params.page == 3

    def test_query_too_short_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError, match="String should have at least 3"):
            UnsplashSearchParams(query="ab")

    def test_model_dump_contains_all_fields(self) -> None:
        params = UnsplashSearchParams(query="nature")
        dumped = params.model_dump()
        assert "query" in dumped
        assert "per_page" in dumped
        assert "orientation" in dumped
        assert "content_filter" in dumped
        assert "page" in dumped
        assert "order_by" in dumped


class TestUnsplashSearchResponse:
    def test_empty_results(self) -> None:
        response = UnsplashSearchResponse(total=0, total_pages=0)
        assert response.total == 0
        assert response.total_pages == 0
        assert response.results == []

    def test_with_results(self) -> None:
        response = UnsplashSearchResponse(
            total=1,
            total_pages=1,
            results=[UnsplashPhoto(**_make_photo())],
        )
        assert len(response.results) == 1
        assert response.results[0].id == "photo-1"

    def test_model_validate_from_dict(self) -> None:
        data = {
            "total": 2,
            "total_pages": 1,
            "results": [_make_photo(id="p1"), _make_photo(id="p2")],
        }
        response = UnsplashSearchResponse.model_validate(data)
        assert response.total == 2
        assert len(response.results) == 2
        assert response.results[0].id == "p1"
        assert response.results[1].id == "p2"
