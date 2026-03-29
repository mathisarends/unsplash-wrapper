import logging
import os

import httpx

from unsplash_wrapper.exceptions import (
    UnsplashAuthenticationException,
    UnsplashClientException,
    UnsplashNotFoundException,
    UnsplashRateLimitException,
    UnsplashServerException,
    UnsplashTimeoutException,
)
from unsplash_wrapper.search import (
    UnsplashPhoto,
    UnsplashSearchParams,
    UnsplashSearchResponse,
)
from unsplash_wrapper.utils.decorators import with_retry

logger = logging.getLogger(__name__)


class UnsplashClient:
    def __init__(self, access_key: str | None = None) -> None:
        self._access_key = access_key or os.getenv("UNSPLASH_API_KEY")
        self._base_url = "https://api.unsplash.com"
        self._headers = {
            "Authorization": f"Client-ID {self._access_key}",
            "Accept-Version": "v1",
        }
        self._client: httpx.AsyncClient | None = None

        if not self._access_key:
            error_msg = (
                "No Unsplash API key provided. "
                "Set UNSPLASH_API_KEY environment variable or pass access_key parameter."
            )
            logger.error(error_msg)
            raise UnsplashAuthenticationException(error_msg)

    async def __aenter__(self) -> "UnsplashClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=10.0,
        )
        return self

    async def __aexit__(self, *_) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        retry_on_exceptions=(UnsplashRateLimitException,),
    )
    async def search_photos(self, params: UnsplashSearchParams) -> list[UnsplashPhoto]:
        logger.info(
            f"Searching photos: query='{params.query}', "
            f"per_page={params.per_page}, "
            f"orientation={params.orientation.value}, "
            f"page={params.page}"
        )

        owned = self._client is None
        client = self._client or httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=10.0,
        )

        try:
            logger.debug(f"Making request to {self._base_url}/search/photos")

            response = await client.get(
                "/search/photos",
                params=params.model_dump(),
            )
            response.raise_for_status()

            logger.debug(f"Response status: {response.status_code}")

            data = response.json()
            search_response = UnsplashSearchResponse.model_validate(data)

            logger.info(
                f"Search successful: found {search_response.total} photos "
                f"({len(search_response.results)} returned, "
                f"{search_response.total_pages} pages total)"
            )

            if search_response.total == 0:
                logger.warning(f"No photos found for query: '{params.query}'")

            return search_response.results

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout after 10s for query '{params.query}': {e}")
            raise UnsplashTimeoutException(
                "Request timeout after 10s", query=params.query
            ) from e

        except httpx.HTTPStatusError as e:
            self._handle_http_status_error(params, e)

        except httpx.HTTPError as e:
            logger.error(f"Unsplash API error for query '{params.query}': {e}")
            raise UnsplashClientException(
                f"HTTP error: {e!s}", query=params.query
            ) from e

        except Exception as e:
            logger.error(
                f"Unexpected error during photo search for query '{params.query}': {e}",
                exc_info=True,
            )
            raise

        finally:
            if owned:
                await client.aclose()

    def _handle_http_status_error(
        self, params: UnsplashSearchParams, e: httpx.HTTPStatusError
    ) -> None:
        status_code = e.response.status_code
        logger.error(f"HTTP error {status_code} for query '{params.query}': {e}")

        if status_code == 401:
            raise UnsplashAuthenticationException(
                "Invalid or missing access key", query=params.query
            ) from e

        elif status_code == 404:
            raise UnsplashNotFoundException(
                "Resource not found", query=params.query
            ) from e

        elif status_code == 429:
            retry_after = e.response.headers.get("Retry-After")
            raise UnsplashRateLimitException(
                "Rate limit exceeded",
                query=params.query,
                retry_after=int(retry_after) if retry_after else None,
            ) from e

        elif 500 <= status_code < 600:
            raise UnsplashServerException(
                f"Server error: {status_code}",
                query=params.query,
                status_code=status_code,
            ) from e

        else:
            raise UnsplashClientException(
                f"Client error: {status_code}",
                query=params.query,
                status_code=status_code,
            ) from e
