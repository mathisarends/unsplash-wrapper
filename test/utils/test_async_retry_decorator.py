import logging
from unittest.mock import AsyncMock, patch

import pytest

from unsplash_client.utils.decorators import async_retry


class LoggingMixinMock:
    logger: logging.Logger = logging.getLogger("test")


@pytest.mark.asyncio
async def test_async_retry_succeeds_on_first_attempt() -> None:
    call_count: int = 0

    @async_retry(max_retries=3)
    async def successful_function() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result: str = await successful_function()

    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_async_retry_succeeds_after_failures() -> None:
    call_count: int = 0

    @async_retry(max_retries=3, initial_delay=0.01, backoff_factor=1.0)
    async def eventually_successful_function() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Not yet")
        return "success"

    result: str = await eventually_successful_function()

    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_async_retry_exhausts_retries() -> None:
    call_count: int = 0

    @async_retry(max_retries=2, initial_delay=0.01)
    async def always_fails_function() -> None:
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError, match="Always fails"):
        await always_fails_function()

    assert call_count == 3


@pytest.mark.asyncio
async def test_async_retry_respects_retry_on_exceptions() -> None:
    call_count: int = 0

    @async_retry(
        max_retries=3,
        retry_on_exceptions=(ValueError,),
        initial_delay=0.01,
    )
    async def selective_retry_function() -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("Retryable")
        raise TypeError("Not retryable")

    with pytest.raises(TypeError, match="Not retryable"):
        await selective_retry_function()

    assert call_count == 2


@pytest.mark.asyncio
async def test_async_retry_with_method_and_logger() -> None:
    mock_instance: LoggingMixinMock = LoggingMixinMock()
    call_count: int = 0

    @async_retry(max_retries=2, initial_delay=0.01, backoff_factor=1.0)
    async def method_with_retry(self: LoggingMixinMock) -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Retry me")
        return "success"

    with (
        patch.object(mock_instance.logger, "warning") as mock_warning,
        patch.object(mock_instance.logger, "info") as mock_info,
    ):
        result: str = await method_with_retry(mock_instance)

        assert result == "success"
        assert call_count == 2
        assert mock_warning.called
        assert mock_info.called


@pytest.mark.asyncio
async def test_async_retry_backoff_factor() -> None:
    call_times: list[float] = []
    current_time: float = 0.0

    @async_retry(
        max_retries=2,
        initial_delay=0.1,
        backoff_factor=2.0,
    )
    async def always_fails_with_timing() -> None:
        call_times.append(current_time)
        raise ValueError("Fail")

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:

        async def side_effect(delay: float) -> None:
            nonlocal current_time
            current_time += delay

        mock_sleep.side_effect = side_effect

        with pytest.raises(ValueError):
            await always_fails_with_timing()

        assert len(mock_sleep.call_args_list) == 2
        first_delay: float = mock_sleep.call_args_list[0][0][0]
        second_delay: float = mock_sleep.call_args_list[1][0][0]

        assert first_delay == 0.1
        assert second_delay == 0.2


@pytest.mark.asyncio
async def test_async_retry_without_logger() -> None:
    call_count: int = 0

    @async_retry(max_retries=1, initial_delay=0.01)
    async def function_without_logger() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Retry")
        return "success"

    result: str = await function_without_logger()

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_async_retry_extracts_logger_from_instance() -> None:
    mock_instance: LoggingMixinMock = LoggingMixinMock()
    call_count: int = 0

    @async_retry(max_retries=2, initial_delay=0.01)
    async def method_with_instance(self: LoggingMixinMock) -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Fail")
        return "success"

    with patch.object(mock_instance.logger, "debug"):
        result: str = await method_with_instance(mock_instance)

        assert result == "success"


@pytest.mark.asyncio
async def test_async_retry_with_kwargs() -> None:
    call_count: int = 0

    @async_retry(max_retries=2, initial_delay=0.01)
    async def function_with_args(value: int, keyword: str = "default") -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Retry")
        return f"{value}:{keyword}"

    result: str = await function_with_args(42, keyword="custom")

    assert result == "42:custom"
    assert call_count == 2


@pytest.mark.asyncio
async def test_async_retry_preserves_function_metadata() -> None:
    @async_retry()
    async def documented_function(value: int) -> int:
        return value * 2

    assert documented_function.__name__ == "documented_function"
