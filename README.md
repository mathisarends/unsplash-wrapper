Unsplash Wrapper
================

Typed async Python client for the [Unsplash API](https://unsplash.com/documentation) focused on the photo search endpoint.

Features:

- Async HTTP via `httpx`
- Pydantic models (requests & responses)
- Fluent builder (`UnsplashSearchParamsBuilder`) OR direct kwargs
- Returns a simple `list[UnsplashPhoto]`
- Automatic retry of 429 (rate limit) responses

Installation
------------

Requires Python 3.13+.

```bash
pip install unsplash-wrapper
```

Set your Unsplash access key (Create one in your Unsplash developer dashboard):

```bash
export UNSPLASH_API_KEY=your_access_key_here  # macOS/Linux
$env:UNSPLASH_API_KEY='your_access_key_here'  # PowerShell
```

Quick Start (async context manager)
------------------------------------

```python
from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder

params = UnsplashSearchParamsBuilder().query("mountains").build()

async with UnsplashClient() as client:
    photos = await client.search_photos(params)

for photo in photos:
    print(photo.id, photo.url)
```

Without Context Manager
-----------------------

`UnsplashClient` can also be used without `async with` — it creates and closes an
`httpx.AsyncClient` per call automatically:

```python
from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder

params = UnsplashSearchParamsBuilder().query("ocean").build()

client = UnsplashClient()
photos = await client.search_photos(params)

for photo in photos:
    print(photo.id, photo.url)
```

Sync Usage Helper
-----------------

If you're not already inside an async context:

```python
import asyncio
from unsplash_wrapper import UnsplashClient, UnsplashSearchParamsBuilder

def main() -> None:
    params = UnsplashSearchParamsBuilder().query("ocean").build()
    photos = asyncio.run(UnsplashClient().search_photos(params))
    for p in photos:
        print(p.id, p.url)

if __name__ == "__main__":
    main()
```

Search Parameter Builder
------------------------

All builder methods are chainable. Pass the result of `.build()` to `search_photos`.

```python
from unsplash_wrapper import (
    UnsplashClient,
    UnsplashSearchParamsBuilder,
)

params = (
    UnsplashSearchParamsBuilder()
    .query("sunset beach")
    .limit(20)
    .landscape_orientation()
    .high_quality()
    .order_by_latest()
    .page(2)
    .build()
)

async with UnsplashClient() as client:
    photos = await client.search_photos(params)

for photo in photos:
    print(photo.id, photo.description, photo.url)
```

Available builder methods:

| Method | Description |
|---|---|
| `.query(str)` | Search query |
| `.limit(int)` | Results per page (default: 10) |
| `.page(int)` | Page number (default: 1) |
| `.orientation(Orientation)` | Set orientation enum directly |
| `.landscape_orientation()` | Shortcut for landscape |
| `.portrait_orientation()` | Shortcut for portrait |
| `.squarish_orientation()` | Shortcut for squarish |
| `.content_filter(ContentFilter)` | Set filter enum directly |
| `.high_quality()` | Shortcut for high content filter |
| `.low_quality()` | Shortcut for low content filter |
| `.order_by(OrderBy)` | Set order enum directly |
| `.order_by_relevant()` | Shortcut for relevance ordering |
| `.order_by_latest()` | Shortcut for latest ordering |

Manual Params
-------------

```python
from unsplash_wrapper import UnsplashSearchParams, UnsplashClient, Orientation

params = UnsplashSearchParams(query="minimal", per_page=5, orientation=Orientation.SQUARISH)

async with UnsplashClient() as client:
    photos = await client.search_photos(params)
```

Models Overview
---------------

`UnsplashPhoto` attributes:

```
id: str
description: str | None
alt_description: str | None
urls: UnsplashUrls (raw/full/regular/small/thumb)
user: UnsplashUser (username, name, portfolio_url, ...)
width, height, color, likes, created_at
url (property -> regular URL string)
```

Error Handling
--------------

Exceptions from `unsplash_wrapper.exceptions`:

- `UnsplashAuthenticationException` (401)
- `UnsplashNotFoundException` (404)
- `UnsplashRateLimitException` (429) — includes `retry_after` if provided
- `UnsplashServerException` (5xx)
- `UnsplashClientException` (other 4xx)
- `UnsplashTimeoutException` (request timeout)

```python
from unsplash_wrapper import (
    UnsplashClient,
    UnsplashRateLimitException,
    UnsplashAuthenticationException,
)

client = UnsplashClient()
try:
    photos = await client.search_photos(query="forest")
except UnsplashRateLimitException as e:
    msg = f"retry after {e.retry_after}s" if e.retry_after else "no retry window"
    print("Rate limited:", msg)
except UnsplashAuthenticationException:
    print("Invalid API key configured")
```

Retry Behavior
--------------

429 responses are retried up to 3 times (delays: 1s → 2s → 4s). Other failures propagate immediately.

Logging
-------

Logger name: `unsplash_wrapper.UnsplashClient`

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Development
-----------

Run tests:

```bash
uv run pytest -q
```

Type check (if mypy configured):

```bash
mypy unsplash_wrapper
```
