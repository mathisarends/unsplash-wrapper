"""
Basic photo search using the builder API.

Run:
    export UNSPLASH_API_KEY=your_key_here
    python examples/01_basic_search.py
"""

import asyncio

from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder


async def main() -> None:
    params = UnsplashSearchParamsBuilder().query("mountains").build()

    async with UnsplashClient() as client:
        photos = await client.search_photos(params)

    for photo in photos:
        print(f"{photo.id}  |  {photo.alt_description}  |  {photo.url}")


if __name__ == "__main__":
    asyncio.run(main())
