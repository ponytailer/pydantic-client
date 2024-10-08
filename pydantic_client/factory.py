from pydantic_client.schema.client_config import ClientConfig


class PydanticClientFactory:
    def __init__(self):
        # name: client_class
        self.pydantic_clients = {}
        # self.config = config

    def register(
        self,
        client_config: ClientConfig
    ):
        def wrapper(protocol_class):
            from pydantic_client.main import PydanticClient

            client = PydanticClient(client_config)

            self.pydantic_clients[protocol_class] = client \
                .bind_client(client_config.get_client()) \
                .bind_protocol(protocol_class) \
                .build()

            return protocol_class

        return wrapper

    def get_client(self, protocol_class=None):
        if len(self.pydantic_clients) == 1:
            return self.pydantic_clients[list(self.pydantic_clients.keys())[0]]
        if not protocol_class:
            raise ValueError(
                "Multiple clients exists, protocol_class is required")
        client = self.pydantic_clients.get(protocol_class)
        if not client:
            raise ValueError(f"client for {protocol_class} not found")
        return client
