from pydantic_client.decorators import delete, get, patch, post, put
from pydantic_client.main import PydanticClient
from pydantic_client.schema.client_config import ClientConfig

__all__ = [
    "PydanticClient",
    "ClientConfig",
    "patch",
    "get",
    "post",
    "put",
    "delete",
]
