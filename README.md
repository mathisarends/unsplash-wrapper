Unsplash Client
================

Lightweight, typed Python client for the [Unsplash API](https://unsplash.com/documentation) focusing on the photo search endpoint. Includes:

- Async HTTP powered by `httpx`
- Pydantic models for responses & request params
- A fluent builder (`UnsplashSearchParamsBuilder`) for ergonomic query construction
- Direct kwargs usage if you prefer no builder
- Automatic retry on rate-limit responses (429) via the `async_retry` decorator

Installation
------------

Requires Python 3.13+.

```bash
pip install unsplash-client
```

Set your Unsplash access key (Create one in your Unsplash developer dashboard):

```bash
export UNSPLASH_API_KEY=your_access_key_here  # macOS/Linux
$env:UNSPLASH_API_KEY='your_access_key_here'  # PowerShell
```

Quick Start
-----------

```python
from unsplash_client import UnsplashClient

client = UnsplashClient()  # Uses UNSPLASH_API_KEY from environment
response = await client.search_photos(query="mountains")

print("Total found:", response.total)
for photo in response.results:
	print(photo.id, photo.url)
```

Search Parameter Options
------------------------

You can provide parameters in two styles: Builder or Raw kwargs.

### 1. Builder style

```python
from unsplash_client import (
	UnsplashClient,
	UnsplashSearchParamsBuilder,
	Orientation,
	ContentFilter,
	OrderBy,
)

builder = (
	UnsplashSearchParamsBuilder()
	.with_query("sunset beach")
	.with_limit(20)
	.with_landscape_orientation()
	.with_high_quality()
	.with_order_by_latest()
	.with_page(2)
)

params = builder.build()
client = UnsplashClient()
response = await client.search_photos(params)

print(f"Returned {len(response.results)} of {response.total} total")
```

### 2. Direct kwargs style

All fields mirror the Pydantic model `UnsplashSearchParams`:

```python
from unsplash_client import UnsplashClient, Orientation, ContentFilter, OrderBy

client = UnsplashClient()
response = await client.search_photos(
	query="architecture",
	per_page=15,
	orientation=Orientation.PORTRAIT,
	content_filter=ContentFilter.HIGH,
	page=1,
	order_by=OrderBy.RELEVANT,
)

for p in response.results:
	print(p.id, p.user.username)
```

Models Overview
---------------

```python
from unsplash_client import UnsplashSearchResponse

# UnsplashSearchResponse fields:
# total: int               -> total matching results
# total_pages: int         -> number of pages available
# results: list[UnsplashPhoto]
#
# UnsplashPhoto exposes convenient properties like:
# photo.url (regular size URL)
```

Error Handling
--------------

The client raises typed exceptions from `unsplash_client.exceptions`:

- `UnsplashAuthenticationException` – missing/invalid key (401)
- `UnsplashNotFoundException` – resource not found (404)
- `UnsplashRateLimitException` – rate limited (429) (contains `retry_after` if provided)
- `UnsplashServerException` – server error 5xx
- `UnsplashClientException` – other 4xx errors
- `UnsplashTimeoutException` – request timed out

Example:

```python
from unsplash_client import (
	UnsplashClient,
	UnsplashRateLimitException,
	UnsplashAuthenticationException,
)

client = UnsplashClient()

try:
	response = await client.search_photos(query="forest")
except UnsplashRateLimitException as e:
	if e.retry_after:
		print(f"Rate limited; retry after {e.retry_after}s")
	else:
		print("Rate limited; no retry window provided")
except UnsplashAuthenticationException:
	print("Invalid API key configured")
```

Retry Behavior
--------------

`search_photos` automatically retries 429 responses up to 3 times with exponential backoff (1s, 2s, 4s). Other errors fail fast.

Logging
-------

The client uses a library-specific logger name: `unsplash_client.UnsplashClient`. Attach handlers or configure globally:

```python
import logging

logging.basicConfig(level=logging.INFO)
```

Advanced: Custom Param Object
------------------------------

If you need to construct params manually (validation enforced):

```python
from unsplash_client import UnsplashSearchParams, Orientation

params = UnsplashSearchParams(query="minimal", per_page=5, orientation=Orientation.SQUARISH)
client = UnsplashClient()
response = await client.search_photos(params)
```

Development
-----------

Run tests:

```bash
uv run pytest -q
```

Type check (if mypy configured):

```bash
mypy unsplash_client
```
