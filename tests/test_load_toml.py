from pydantic_client.clients.requests import RequestsClient
from pydantic_client.schema.ClientConfig import ClientConfig


def test_load_toml():
    config = ClientConfig.load_toml("tests/config.toml")
    assert config.base_url == "http://localhost"
    assert config.headers == {"authorization": "Bearer xxxxxx", "keepalive": 30}

    client = RequestsClient.from_toml(config)
    assert client.base_url == "http://localhost"
    assert client.headers == {"authorization": "Bearer xxxxxx", "keepalive": 30}
