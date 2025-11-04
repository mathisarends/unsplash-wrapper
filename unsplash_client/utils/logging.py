import logging
import os
from typing import ClassVar

from dotenv import load_dotenv

load_dotenv(override=True)

LIBRARY_NAME = "unsplash_client"
NOISY_LOGGERS = ["httpx", "httpcore", "httpcore.connection", "httpcore.http11"]

logger = logging.getLogger(LIBRARY_NAME)
logger.addHandler(logging.NullHandler())


def configure_library_logging(level: str = "WARNING") -> None:
    log_level = getattr(logging, level.upper(), logging.WARNING)
    library_logger = logging.getLogger(LIBRARY_NAME)

    if library_logger.handlers:
        library_logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    library_logger.setLevel(log_level)
    library_logger.addHandler(handler)

    _suppress_noisy_third_party_loggers()


def _suppress_noisy_third_party_loggers() -> None:
    for logger_name in NOISY_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def _auto_configure_from_environment() -> None:
    env_log_level = os.getenv("NOTIONARY_LOG_LEVEL")
    if env_log_level:
        configure_library_logging(env_log_level)


_auto_configure_from_environment()


class LoggingMixin:
    logger: ClassVar[logging.Logger] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.logger = logging.getLogger(f"{LIBRARY_NAME}.{cls.__name__}")