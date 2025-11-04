import os
import pytest
from unittest.mock import Mock, patch
import httpx

from unsplash_client.exceptions import UnsplashAuthenticationException, UnsplashClientException, UnsplashNotFoundException, UnsplashRateLimitException, UnsplashServerException
from unsplash_client.search.models import ContentFilter, OrderBy, Orientation, UnsplashSearchParams
from unsplash_client.service import UnsplashClient



@pytest.fixture
def sample_params() -> UnsplashSearchParams:
    return UnsplashSearchParams(
        query="test",
        per_page=10,
        orientation=Orientation.LANDSCAPE,
        content_filter=ContentFilter.HIGH,
        page=1,
        order_by=OrderBy.RELEVANT,
    )


def test_init_with_access_key() -> None:
    client = UnsplashClient(access_key="test_key")
    assert client.access_key == "test_key"
    assert client._base_url == "https://api.unsplash.com"


def test_init_without_access_key_uses_env() -> None:
    with patch.dict(os.environ, {"UNSPLASH_ACCESS_KEY": "env_key"}):
        client = UnsplashClient()
        assert client.access_key == "env_key"


def test_init_without_access_key_and_no_env() -> None:
    with patch.dict(os.environ, {}, clear=True):
        client = UnsplashClient()
        assert client.access_key is None


@pytest.mark.asyncio
async def test_handle_http_error_401(sample_params: UnsplashSearchParams) -> None:
    client = UnsplashClient(access_key="test_key")
    
    mock_response = Mock()
    mock_response.status_code = 401
    error = httpx.HTTPStatusError("Unauthorized", request=Mock(), response=mock_response)
    
    with pytest.raises(UnsplashAuthenticationException) as exc_info:
        client._handle_http_error(sample_params, error)
    
    assert exc_info.value.query == "test"
    assert "access key" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_handle_http_error_404(sample_params: UnsplashSearchParams) -> None:
    client = UnsplashClient(access_key="test_key")
    
    mock_response = Mock()
    mock_response.status_code = 404
    error = httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
    
    with pytest.raises(UnsplashNotFoundException):
        client._handle_http_error(sample_params, error)


@pytest.mark.asyncio
async def test_handle_http_error_429_with_retry_after(sample_params: UnsplashSearchParams) -> None:
    client = UnsplashClient(access_key="test_key")
    
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}
    error = httpx.HTTPStatusError("Rate Limited", request=Mock(), response=mock_response)
    
    with pytest.raises(UnsplashRateLimitException) as exc_info:
        client._handle_http_error(sample_params, error)
    
    assert exc_info.value.retry_after == 60


@pytest.mark.asyncio
async def test_handle_http_error_429_without_retry_after(sample_params: UnsplashSearchParams) -> None:
    client = UnsplashClient(access_key="test_key")
    
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {}
    error = httpx.HTTPStatusError("Rate Limited", request=Mock(), response=mock_response)
    
    with pytest.raises(UnsplashRateLimitException) as exc_info:
        client._handle_http_error(sample_params, error)
    
    assert exc_info.value.retry_after is None


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
async def test_handle_http_error_5xx(sample_params: UnsplashSearchParams, status_code: int) -> None:
    client = UnsplashClient(access_key="test_key")
    
    mock_response = Mock()
    mock_response.status_code = status_code
    error = httpx.HTTPStatusError("Server Error", request=Mock(), response=mock_response)
    
    with pytest.raises(UnsplashServerException) as exc_info:
        client._handle_http_error(sample_params, error)
    
    assert exc_info.value.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [400, 403, 422])
async def test_handle_http_error_4xx(sample_params: UnsplashSearchParams, status_code: int) -> None:
    client = UnsplashClient(access_key="test_key")
    
    mock_response = Mock()
    mock_response.status_code = status_code
    error = httpx.HTTPStatusError("Client Error", request=Mock(), response=mock_response)
    
    with pytest.raises(UnsplashClientException) as exc_info:
        client._handle_http_error(sample_params, error)
    
    assert exc_info.value.status_code == status_code



def test_logs_warning_when_no_access_key() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with patch("logging.getLogger") as mock_get_logger:
            logger_instance = Mock()
            mock_get_logger.return_value = logger_instance
            
            UnsplashClient()
            
            assert logger_instance.warning.called
            warning_call = str(logger_instance.warning.call_args)
            assert "access key" in warning_call.lower()


def test_logs_debug_when_access_key_provided() -> None:
    with patch("logging.getLogger") as mock_get_logger:
        logger_instance = Mock()
        mock_get_logger.return_value = logger_instance
        
        UnsplashClient(access_key="test_key")
        
        assert logger_instance.debug.called