from unittest.mock import AsyncMock, patch

import httpx
import pytest

from unsplash_wrapper.client import UnsplashClient
from unsplash_wrapper.exceptions import (
    UnsplashAuthenticationException,
    UnsplashClientException,
    UnsplashNotFoundException,
    UnsplashRateLimitException,
    UnsplashServerException,
    UnsplashTimeoutException,
)
from unsplash_wrapper.search.models import (
    UnsplashSearchParams,
)

VALID_URL = "https://images.unsplash.com/photo-1"
FAKE_KEY = "test-access-key-12345"


def _make_photo_dict(**overrides: object) -> dict:
    base = {
        "id": "photo-1",
        "description": "A test photo",
        "alt_description": "alt text",
        "urls": {
            "raw": VALID_URL,
            "full": VALID_URL,
            "regular": VALID_URL,
            "small": VALID_URL,
            "thumb": VALID_URL,
        },
        "user": {
            "id": "user-1",
            "username": "testuser",
            "name": "Test User",
        },
        "width": 1920,
        "height": 1080,
        "color": "#ffffff",
        "likes": 42,
        "created_at": "2025-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def _make_search_response(count: int = 1) -> dict:
    return {
        "total": count,
        "total_pages": 1,
        "results": [_make_photo_dict(id=f"photo-{i}") for i in range(count)],
    }


def _make_params(**overrides: object) -> UnsplashSearchParams:
    defaults = {"query": "mountains"}
    defaults.update(overrides)
    return UnsplashSearchParams(**defaults)


def _make_httpx_response(
    status_code: int = 200,
    json_data: dict | None = None,
    headers: dict | None = None,
) -> httpx.Response:
    response = httpx.Response(
        status_code=status_code,
        json=json_data,
        headers=headers or {},
        request=httpx.Request("GET", "https://api.unsplash.com/search/photos"),
    )
    return response


class TestUnsplashClientInit:
    def test_init_with_explicit_access_key(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        assert client._access_key == FAKE_KEY

    def test_init_with_env_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("UNSPLASH_API_KEY", "env-key-123")
        client = UnsplashClient()
        assert client._access_key == "env-key-123"

    def test_init_without_key_raises_authentication_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("UNSPLASH_API_KEY", raising=False)
        with pytest.raises(
            UnsplashAuthenticationException, match="No Unsplash API key"
        ):
            UnsplashClient()

    def test_init_sets_headers_with_access_key(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        assert client._headers["Authorization"] == f"Client-ID {FAKE_KEY}"
        assert client._headers["Accept-Version"] == "v1"

    def test_init_sets_base_url(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        assert client._base_url == "https://api.unsplash.com"

    def test_client_starts_as_none(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        assert client._client is None


class TestUnsplashClientContextManager:
    async def test_aenter_creates_httpx_client(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        async with client as c:
            assert c._client is not None
            assert isinstance(c._client, httpx.AsyncClient)

    async def test_aexit_closes_client(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        async with client:
            pass
        assert client._client is None

    async def test_aenter_returns_self(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        async with client as c:
            assert c is client


class TestUnsplashClientSearchPhotosSuccess:
    async def test_returns_photos_on_success(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        mock_response = _make_httpx_response(
            status_code=200, json_data=_make_search_response(2)
        )

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(return_value=mock_response)
        mock_httpx_client.aclose = AsyncMock()

        with patch(
            "unsplash_wrapper.client.httpx.AsyncClient", return_value=mock_httpx_client
        ):
            results = await client.search_photos(_make_params())

        assert len(results) == 2
        assert results[0].id == "photo-0"
        assert results[1].id == "photo-1"

    async def test_search_with_context_manager(self) -> None:
        mock_response = _make_httpx_response(
            status_code=200, json_data=_make_search_response(1)
        )

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(return_value=mock_response)
        mock_httpx_client.aclose = AsyncMock()

        with patch(
            "unsplash_wrapper.client.httpx.AsyncClient", return_value=mock_httpx_client
        ):
            async with UnsplashClient(access_key=FAKE_KEY) as client:
                results = await client.search_photos(_make_params())

        assert len(results) == 1

    async def test_empty_search_results(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        mock_response = _make_httpx_response(
            status_code=200, json_data=_make_search_response(0)
        )

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(return_value=mock_response)
        mock_httpx_client.aclose = AsyncMock()

        with patch(
            "unsplash_wrapper.client.httpx.AsyncClient", return_value=mock_httpx_client
        ):
            results = await client.search_photos(_make_params())

        assert results == []

    async def test_passes_params_to_httpx(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        params = _make_params(query="cats", per_page=5)
        mock_response = _make_httpx_response(
            status_code=200, json_data=_make_search_response(0)
        )

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(return_value=mock_response)
        mock_httpx_client.aclose = AsyncMock()

        with patch(
            "unsplash_wrapper.client.httpx.AsyncClient", return_value=mock_httpx_client
        ):
            await client.search_photos(params)

        mock_httpx_client.get.assert_called_once_with(
            "/search/photos",
            params=params.model_dump(),
        )


class TestUnsplashClientSearchPhotosTimeout:
    async def test_timeout_raises_unsplash_timeout_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.ReadTimeout("Connection timed out")
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashTimeoutException, match="Request timeout"),
        ):
            await client.search_photos(_make_params())

    async def test_timeout_exception_has_query(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(side_effect=httpx.ReadTimeout("timed out"))
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashTimeoutException) as exc_info,
        ):
            await client.search_photos(_make_params(query="sunset"))

        assert exc_info.value.query == "sunset"


class TestUnsplashClientSearchPhotosHttpErrors:
    async def test_401_raises_authentication_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        response = _make_httpx_response(
            status_code=401, json_data={"errors": ["Unauthorized"]}
        )

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "401 Unauthorized", request=response.request, response=response
            )
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(
                UnsplashAuthenticationException, match="Invalid or missing access key"
            ),
        ):
            await client.search_photos(_make_params())

    async def test_404_raises_not_found_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        response = _make_httpx_response(status_code=404)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "404 Not Found", request=response.request, response=response
            )
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashNotFoundException, match="Resource not found"),
        ):
            await client.search_photos(_make_params())

    async def test_429_raises_rate_limit_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        response = _make_httpx_response(status_code=429, headers={"Retry-After": "30"})

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "429 Too Many Requests", request=response.request, response=response
            )
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashRateLimitException) as exc_info,
        ):
            await client.search_photos(_make_params())

        assert exc_info.value.retry_after == 30

    async def test_429_without_retry_after_header(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        response = _make_httpx_response(status_code=429)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "429 Too Many Requests", request=response.request, response=response
            )
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashRateLimitException) as exc_info,
        ):
            await client.search_photos(_make_params())

        assert exc_info.value.retry_after is None

    async def test_500_raises_server_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        response = _make_httpx_response(status_code=500)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "500 Internal Server Error", request=response.request, response=response
            )
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashServerException, match="Server error: 500"),
        ):
            await client.search_photos(_make_params())

    async def test_502_raises_server_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        response = _make_httpx_response(status_code=502)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "502 Bad Gateway", request=response.request, response=response
            )
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashServerException) as exc_info,
        ):
            await client.search_photos(_make_params())

        assert exc_info.value.status_code == 502

    async def test_403_raises_client_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        response = _make_httpx_response(status_code=403)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "403 Forbidden", request=response.request, response=response
            )
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashClientException, match="Client error: 403"),
        ):
            await client.search_photos(_make_params())

    async def test_generic_http_error_raises_client_exception(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashClientException, match="HTTP error"),
        ):
            await client.search_photos(_make_params())


class TestUnsplashClientSearchPhotosOwnedClient:
    async def test_closes_owned_client_on_success(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)
        mock_response = _make_httpx_response(
            status_code=200, json_data=_make_search_response(1)
        )

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(return_value=mock_response)
        mock_httpx_client.aclose = AsyncMock()

        with patch(
            "unsplash_wrapper.client.httpx.AsyncClient", return_value=mock_httpx_client
        ):
            await client.search_photos(_make_params())

        mock_httpx_client.aclose.assert_called_once()

    async def test_closes_owned_client_on_error(self) -> None:
        client = UnsplashClient(access_key=FAKE_KEY)

        mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        mock_httpx_client.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        mock_httpx_client.aclose = AsyncMock()

        with (
            patch(
                "unsplash_wrapper.client.httpx.AsyncClient",
                return_value=mock_httpx_client,
            ),
            pytest.raises(UnsplashClientException),
        ):
            await client.search_photos(_make_params())

        mock_httpx_client.aclose.assert_called_once()
