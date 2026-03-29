"""
Demonstrates all available builder options: orientation, ordering, pagination, quality filter.

Run:
    export UNSPLASH_API_KEY=your_key_here
    python examples/02_builder_options.py
"""

import asyncio

from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder


async def main() -> None:
    params = (
        UnsplashSearchParamsBuilder()
        .query("sunset beach")
        .limit(5)
        .landscape_orientation()
        .high_quality()
        .order_by_latest()
        .page(1)
        .build()
    )

    async with UnsplashClient() as client:
        photos = await client.search_photos(params)

    print(f"Found {len(photos)} photos\n")
    for photo in photos:
        print(f"  id          : {photo.id}")
        print(f"  description : {photo.description or photo.alt_description}")
        print(f"  photographer: {photo.user.name} (@{photo.user.username})")
        print(f"  size        : {photo.width}x{photo.height}")
        print(f"  likes       : {photo.likes}")
        print(f"  url         : {photo.url}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
