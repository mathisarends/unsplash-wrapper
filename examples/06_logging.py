"""
Enable verbose logging to see request/response details from the client.

Run:
    export UNSPLASH_API_KEY=your_key_here
    python examples/06_logging.py
"""

import asyncio
import logging

# INFO shows summaries; DEBUG shows full request details
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(name)s: %(message)s",
)

from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder  # noqa: E402


async def main() -> None:
    params = UnsplashSearchParamsBuilder().query("ocean waves").limit(3).build()

    async with UnsplashClient() as client:
        photos = await client.search_photos(params)

    print(f"\nResult: {len(photos)} photos")


if __name__ == "__main__":
    asyncio.run(main())
