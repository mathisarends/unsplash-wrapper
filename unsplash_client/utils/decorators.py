import asyncio
import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

FuncType = TypeVar("FuncType", bound=Callable[..., Any])


def async_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: tuple[type[Exception], ...] | None = None,
):
    def decorator(func: FuncType) -> FuncType:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None
            logger = _extract_logger(args)

            for attempt in range(max_retries + 1):
                try:
                    _log_retry_attempt(logger, attempt, max_retries, func.__name__)
                    return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    if not _should_retry_exception(e, retry_on_exceptions):
                        _log_non_retryable_exception(logger, e, func.__name__)
                        raise

                    if attempt == max_retries:
                        _log_max_retries_exceeded(logger, e, func.__name__, max_retries)
                        raise

                    _log_retry_wait(
                        logger, e, func.__name__, attempt, max_retries, delay
                    )
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def _extract_logger(args: tuple[Any, ...]) -> logging.Logger | None:
    if args and hasattr(args[0], "logger"):
        logger = getattr(args[0], "logger", None)
        if isinstance(logger, logging.Logger):
            return logger
    return None


def _should_retry_exception(
    exception: Exception, retry_on_exceptions: tuple[type[Exception], ...] | None
) -> bool:
    if retry_on_exceptions is None:
        return True
    return isinstance(exception, retry_on_exceptions)


def _log_retry_attempt(
    logger: logging.Logger | None, attempt: int, max_retries: int, func_name: str
) -> None:
    if logger and attempt > 0:
        logger.info(f"Retry attempt {attempt}/{max_retries} for {func_name}")


def _log_non_retryable_exception(
    logger: logging.Logger | None, exception: Exception, func_name: str
) -> None:
    if logger:
        logger.debug(f"{func_name} raised {type(exception).__name__}, not retrying")


def _log_max_retries_exceeded(
    logger: logging.Logger | None,
    exception: Exception,
    func_name: str,
    max_retries: int,
) -> None:
    if logger:
        logger.error(f"{func_name} failed after {max_retries} retries: {exception}")


def _log_retry_wait(
    logger: logging.Logger | None,
    exception: Exception,
    func_name: str,
    attempt: int,
    max_retries: int,
    delay: float,
) -> None:
    if logger:
        logger.warning(
            f"{func_name} attempt {attempt + 1}/{max_retries + 1} failed: {exception}. "
            f"Retrying in {delay:.2f}s..."
        )
