import os
from dotenv import load_dotenv
import httpx

from unsplash_client.exceptions import (
    UnsplashAuthenticationException, 
    UnsplashClientException, 
    UnsplashNotFoundException, 
    UnsplashRateLimitException, 
    UnsplashServerException,
    UnsplashTimeoutException
)
from unsplash_client.search import (
    UnsplashSearchResponse,
    UnsplashSearchParams,
)
from unsplash_client.utils.decorators import async_retry
from unsplash_client.utils.logging import LoggingMixin

load_dotenv(override=True)

class UnsplashClient(LoggingMixin):
    def __init__(self, access_key: str | None = None) -> None:
        self.access_key = access_key or os.getenv("UNSPLASH_API_KEY")
        self._base_url = "https://api.unsplash.com"
        
        if not self.access_key:
            self.logger.warning("No Unsplash access key provided")
        else:
            self.logger.debug("UnsplashClient initialized with access key")

    @async_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        retry_on_exceptions=(UnsplashRateLimitException,)
    )
    async def search_photos(
        self, params: UnsplashSearchParams
    ) -> UnsplashSearchResponse:
        self.logger.info(
            f"Searching photos: query='{params.query}', per_page={params.per_page}, "
            f"orientation={params.orientation.value}, page={params.page}"
        )
        
        headers = {
            "Authorization": f"Client-ID {self.access_key}",
            "Accept-Version": "v1",
        }

        async with httpx.AsyncClient() as client:
            try:
                self.logger.debug(f"Making request to {self._base_url}/search/photos")
                
                response = await client.get(
                    f"{self._base_url}/search/photos",
                    params=params.model_dump(),
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                
                self.logger.debug(f"Response status: {response.status_code}")
                
                data = response.json()
                search_response = UnsplashSearchResponse.model_validate(data)
                
                self.logger.info(
                    f"Search successful: found {search_response.total} photos "
                    f"({len(search_response.results)} returned, {search_response.total_pages} pages total)"
                )
                
                if search_response.total == 0:
                    self.logger.warning(f"No photos found for query: '{params.query}'")
                
                return search_response

            except httpx.TimeoutException as e:
                self.logger.error(f"Request timeout after 10s for query '{params.query}': {e}")
                raise UnsplashTimeoutException(
                    "Request timeout after 10s",
                    query=params.query
                ) from e
            
            except httpx.HTTPStatusError as e:
                self._handle_http_error(params, e)
            
            except httpx.HTTPError as e:
                self.logger.error(f"Unsplash API error for query '{params.query}': {e}")
                raise UnsplashClientException(
                    f"HTTP error: {str(e)}",
                    query=params.query
                ) from e
            
            except Exception as e:
                self.logger.error(
                    f"Unexpected error during photo search for query '{params.query}': {e}",
                    exc_info=True
                )
                
                raise

    def _handle_http_error(self, params: UnsplashSearchParams, e: httpx.HTTPStatusError) -> None:
        status_code = e.response.status_code
        self.logger.error(
                    f"HTTP error {status_code} for query '{params.query}': {e}"
                )
                
        if status_code == 401:
            raise UnsplashAuthenticationException(
                        "Invalid or missing access key",
                        query=params.query
                    ) from e
                
        elif status_code == 404:
            raise UnsplashNotFoundException(
                        "Resource not found",
                        query=params.query
                    ) from e
                
        elif status_code == 429:
            retry_after = e.response.headers.get("Retry-After")
            raise UnsplashRateLimitException(
                        "Rate limit exceeded",
                        query=params.query,
                        retry_after=int(retry_after) if retry_after else None
                    ) from e
                
        elif 500 <= status_code < 600:
            raise UnsplashServerException(
                        f"Server error: {status_code}",
                        query=params.query,
                        status_code=status_code
                    ) from e
                
        else:
            raise UnsplashClientException(
                        f"Client error: {status_code}",
                        query=params.query,
                        status_code=status_code
                    ) from e
