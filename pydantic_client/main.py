from typing import Type

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.container import container
from pydantic_client.schema.client_config import ClientConfig


class PydanticClient:
    """

    class User(BaseModel):
        id: int
        name: str

    class WebClient:
        @get("/users/{user_id}")
        def get_user(self, user_id: int) -> User:
            ...

    web_client = PydanticClient.from_toml(...)
        .bind_client(RequestsClient)
        .bind_protocol(WebClient)
        .build()

    # or

    client: WebClient = PydanticClient(
        ClientConfig(
            base_url="https://example.com",
            headers={"Authorization": "Bearer abcdefg"},
            timeout=10
        )
    ).bind_client(RequestsClient)
        .bind_protocol(WebClient)
        .build()

    user: User = web_client.get_user(123)

    """

    def __init__(self, config: ClientConfig):
        self.config = config
        self.client = None
        self.protocol = None

    def bind_client(self, client_class: Type[AbstractClient]):
        self.client = client_class(self.config)
        return self

    def bind_protocol(self, protocol_class, *args, **kwargs):
        self.protocol = protocol_class(*args, **kwargs)
        return self

    def build(self):
        container.bind_protocol(self.protocol, self.client)
        return self.protocol
