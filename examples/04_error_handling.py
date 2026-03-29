"""
Proper error handling for authentication errors, rate limits, and other failures.

Run:
    export UNSPLASH_API_KEY=your_key_here
    python examples/04_error_handling.py
"""

import asyncio
import logging

from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder
from unsplash_wrapper.exceptions import (
    UnsplashAuthenticationException,
    UnsplashClientException,
    UnsplashNotFoundException,
    UnsplashRateLimitException,
    UnsplashServerException,
    UnsplashTimeoutException,
)

logging.basicConfig(level=logging.WARNING)


async def main() -> None:
    params = UnsplashSearchParamsBuilder().query("forest").build()

    try:
        async with UnsplashClient() as client:
            photos = await client.search_photos(params)

        print(f"Got {len(photos)} photos")
        for photo in photos:
            print(f"  {photo.id}  {photo.url}")

    except UnsplashAuthenticationException:
        print("Invalid API key. Set UNSPLASH_API_KEY and try again.")

    except UnsplashRateLimitException as e:
        if e.retry_after:
            print(f"Rate limited. Retry after {e.retry_after}s.")
        else:
            print("Rate limited. No retry window provided.")

    except UnsplashTimeoutException:
        print("Request timed out after 10s.")

    except UnsplashNotFoundException:
        print("Resource not found.")

    except UnsplashServerException as e:
        print(f"Unsplash server error ({e.status_code}).")

    except UnsplashClientException as e:
        print(f"Client error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
