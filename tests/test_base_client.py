from typing import Any, Dict, Optional, Type

from pydantic_client.base import BaseWebClient


class TestBaseWebClient(BaseWebClient):
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type] = None
    ) -> Any:
        return {
            "method": method,
            "path": path,
            "params": params,
            "json": json,
            "response_model": response_model
        }


def test_base_client_initialization():
    client = TestBaseWebClient(
        base_url="http://example.com",
        headers={"Authorization": "Bearer token"},
        timeout=30
    )

    assert client.base_url == "http://example.com"
    assert client.headers == {"Authorization": "Bearer token"}
    assert client.timeout == 30


def test_base_client_from_config():
    config = {
        "base_url": "http://example.com",
        "headers": {"Authorization": "Bearer token"},
        "timeout": 30
    }

    client = TestBaseWebClient.from_config(config)

    assert client.base_url == "http://example.com"
    assert client.headers == {"Authorization": "Bearer token"}
    assert client.timeout == 30


def test_make_url():
    client = TestBaseWebClient(base_url="http://example.com")

    assert client._make_url("/test") == "http://example.com/test"
    assert client._make_url("test") == "http://example.com/test"

    client = TestBaseWebClient(base_url="http://example.com/")
    assert client._make_url("/test") == "http://example.com/test"
