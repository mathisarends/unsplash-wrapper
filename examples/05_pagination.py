"""
Paginate through multiple pages of results.

Run:
    export UNSPLASH_API_KEY=your_key_here
    python examples/05_pagination.py
"""

import asyncio

from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder

QUERY = "city lights"
PAGES = 3
PER_PAGE = 5


async def main() -> None:
    async with UnsplashClient() as client:
        for page in range(1, PAGES + 1):
            params = (
                UnsplashSearchParamsBuilder()
                .query(QUERY)
                .limit(PER_PAGE)
                .page(page)
                .build()
            )
            photos = await client.search_photos(params)
            print(f"--- Page {page} ({len(photos)} photos) ---")
            for photo in photos:
                print(f"  {photo.id}  {photo.url}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
