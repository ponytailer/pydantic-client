from pydantic_client.clients.requests import RequestsClient
from pydantic_client import ClientConfig


def test_load_toml():
    config = ClientConfig.load_toml("tests/config.toml")
    assert config.base_url == "http://localhost:12098"
    assert config.headers == {"authorization": "Bearer xxxxxx"}

    client = RequestsClient.from_toml(config)
    assert config.base_url == "http://localhost:12098"
    assert client.config.headers == {"authorization": "Bearer xxxxxx"}
