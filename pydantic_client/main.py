import logging

from pydantic_client.container import container
from pydantic_client.schema.client_config import ClientConfig

logger = logging.getLogger(__name__)


class PydanticClientManager:
    def __init__(self):
        # proto_class: protocol_object
        self.pydantic_clients = {}

    def register(
        self,
        client_config: ClientConfig
    ):
        def wrapper(protocol_class):
            web_client = client_config.get_client()
            protocol = protocol_class()
            container.bind_protocol(protocol, web_client)
            if protocol_class in self.pydantic_clients:
                logger.warning(
                    f"protocol {protocol_class} already registered, will be overwritten")
            self.pydantic_clients[protocol_class] = protocol
            return protocol_class

        return wrapper

    def get(self, protocol_class=None):
        if len(self.pydantic_clients) == 1:
            return self.pydantic_clients[list(self.pydantic_clients.keys())[0]]
        if not protocol_class:
            raise ValueError(
                "Multiple clients exists, protocol_class is required")
        client = self.pydantic_clients.get(protocol_class)
        if not client:
            raise ValueError(f"client for {protocol_class} not found")
        return client
