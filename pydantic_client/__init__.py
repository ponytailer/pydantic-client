from pydantic_client.decorators import delete, get, patch, post, put
from pydantic_client.main import PydanticClientManager
from pydantic_client.schema.client_config import ClientConfig, ClientType

pydantic_client_manager = PydanticClientManager()

__all__ = [
    "pydantic_client_manager",
    "ClientConfig",
    "ClientType",
    "patch",
    "get",
    "post",
    "put",
    "delete",
]
