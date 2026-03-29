from unittest.mock import AsyncMock

import pytest

import unsplash_wrapper.utils.decorators as dec_module
from unsplash_wrapper.utils.decorators import with_retry


class _RetryableError(Exception):
    pass


class _NonRetryableError(Exception):
    pass


class TestWithRetrySuccess:
    async def test_returns_result_on_first_attempt(self) -> None:
        mock_fn = AsyncMock(return_value="ok")
        decorated = with_retry(max_retries=3)(mock_fn)

        result = await decorated()

        assert result == "ok"
        assert mock_fn.call_count == 1

    async def test_returns_result_after_transient_failure(self) -> None:
        mock_fn = AsyncMock(side_effect=[_RetryableError("fail"), "ok"])
        decorated = with_retry(
            max_retries=3,
            initial_delay=0.0,
            retry_on_exceptions=(_RetryableError,),
        )(mock_fn)

        result = await decorated()

        assert result == "ok"
        assert mock_fn.call_count == 2


class TestWithRetryExhausted:
    async def test_raises_after_max_retries_exceeded(self) -> None:
        mock_fn = AsyncMock(side_effect=_RetryableError("always fails"))
        decorated = with_retry(
            max_retries=2,
            initial_delay=0.0,
            retry_on_exceptions=(_RetryableError,),
        )(mock_fn)

        with pytest.raises(_RetryableError, match="always fails"):
            await decorated()

        assert mock_fn.call_count == 3  # initial + 2 retries


class TestWithRetryNonRetryableException:
    async def test_raises_immediately_for_non_retryable_exception(self) -> None:
        mock_fn = AsyncMock(side_effect=_NonRetryableError("not retryable"))
        decorated = with_retry(
            max_retries=3,
            initial_delay=0.0,
            retry_on_exceptions=(_RetryableError,),
        )(mock_fn)

        with pytest.raises(_NonRetryableError, match="not retryable"):
            await decorated()

        assert mock_fn.call_count == 1


class TestWithRetryAllExceptions:
    async def test_retries_any_exception_when_no_filter(self) -> None:
        mock_fn = AsyncMock(side_effect=[ValueError("oops"), "ok"])
        decorated = with_retry(
            max_retries=3,
            initial_delay=0.0,
            retry_on_exceptions=None,
        )(mock_fn)

        result = await decorated()

        assert result == "ok"
        assert mock_fn.call_count == 2


class TestWithRetryBackoff:
    async def test_delay_increases_with_backoff_factor(self) -> None:
        delays_observed: list[float] = []

        async def fake_sleep(delay: float) -> None:
            delays_observed.append(delay)

        mock_fn = AsyncMock(
            side_effect=[_RetryableError("1"), _RetryableError("2"), "ok"]
        )

        original_sleep = dec_module.asyncio.sleep

        dec_module.asyncio.sleep = fake_sleep  # type: ignore[assignment]
        try:
            decorated = with_retry(
                max_retries=3,
                initial_delay=1.0,
                backoff_factor=2.0,
                retry_on_exceptions=(_RetryableError,),
            )(mock_fn)

            await decorated()
        finally:
            dec_module.asyncio.sleep = original_sleep  # type: ignore[assignment]

        assert len(delays_observed) == 2
        assert delays_observed[0] == pytest.approx(1.0)
        assert delays_observed[1] == pytest.approx(2.0)


class TestWithRetryPreservesFunction:
    async def test_preserves_function_name(self) -> None:
        async def my_function() -> str:
            return "result"

        decorated = with_retry(max_retries=1)(my_function)
        assert decorated.__name__ == "my_function"

    async def test_passes_args_and_kwargs(self) -> None:
        mock_fn = AsyncMock(return_value="ok")
        decorated = with_retry(max_retries=1)(mock_fn)

        await decorated("arg1", key="value")

        mock_fn.assert_called_once_with("arg1", key="value")
