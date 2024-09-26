from pydantic_client.schema.client_config import FactoryConfig


class PydanticClientFactory:
    """
    toml file example:
    [[tools.pydantic_client.factory]]
    name = "book_client
    base_url = "https://example.com/api/v1"
    timeout = 1
    [[tools.pydantic_client.factory]]
    name = "author_client
    base_url = "https://example.com/api/v2"
    timeout = 1
    [[tools.pydantic_client.factory]]
    name = "address_client
    base_url = "https://example.com/api/v3"
    timeout = 1

    factory = PydanticClientFactory.from_toml("pydantic_client.toml") \
        .register_client("book_client", RequestsClient, BookProtocol) \
        .register_client("author_client", HttpxClient, AuthorProtocol)
        .build()

    book: Book = factory.get_client(BookProtocol).get_books(1)

    """

    def __init__(self, config: FactoryConfig):
        # name: client_class
        self.pydantic_clients = {}
        self.config = config

    @classmethod
    def from_toml(cls, toml_file: str) -> "PydanticClientFactory":
        config = FactoryConfig.load_toml(toml_file)
        return cls(config)

    def register_client(
        self,
        client_name: str,
        client_class,
        protocol_class,
        *args,
        **kwargs
    ):
        """
        params:
            client_name: str, name of the client which in toml file.
            client_class: client class which in pydantic-client.
            protocol_class: protocol class which define the routers.
        """
        cfg = self.config.get_by_name(client_name)
        if not cfg:
            raise ValueError(f"client {client_name} not found in config")

        from pydantic_client import PydanticClient

        client = PydanticClient(cfg)

        self.pydantic_clients[protocol_class] = client \
            .bind_client(client_class) \
            .bind_protocol(protocol_class, *args, **kwargs) \
            .build()
        return self

    def build(self):
        return self

    def get_client(self, protocol_class):
        client = self.pydantic_clients.get(protocol_class)
        if not client:
            raise ValueError(f"client for {protocol_class} not found")
        return client
