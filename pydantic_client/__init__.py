from pydantic_client.decorators import delete, get, patch, post, put
from pydantic_client.factory import PydanticClientFactory
from pydantic_client.main import PydanticClient
from pydantic_client.schema.client_config import ClientConfig

pydantic_client_factory = PydanticClientFactory()

__all__ = [
    "pydantic_client_factory",
    "ClientConfig",
    "patch",
    "get",
    "post",
    "put",
    "delete",
]
