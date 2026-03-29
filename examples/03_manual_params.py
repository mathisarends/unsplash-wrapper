"""
Pass search params directly via UnsplashSearchParams instead of the builder.

Run:
    export UNSPLASH_API_KEY=your_key_here
    python examples/03_manual_params.py
"""

import asyncio

from unsplash_wrapper import (
    ContentFilter,
    OrderBy,
    Orientation,
    UnsplashClient,
    UnsplashSearchParams,
)


async def main() -> None:
    params = UnsplashSearchParams(
        query="minimal architecture",
        per_page=5,
        orientation=Orientation.SQUARISH,
        content_filter=ContentFilter.HIGH,
        order_by=OrderBy.RELEVANT,
        page=1,
    )

    async with UnsplashClient() as client:
        photos = await client.search_photos(params)

    for photo in photos:
        print(f"{photo.id}  {photo.url}")


if __name__ == "__main__":
    asyncio.run(main())
