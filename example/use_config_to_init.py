from example.protocol import BookProtocol, Book
from pydantic_client import PydanticClient, ClientConfig
from pydantic_client.clients import RequestsClient

if __name__ == "__main__":
    cfg = ClientConfig(
        base_url="https://example.com/api"
    )
    client = PydanticClient(cfg) \
        .bind_client(RequestsClient) \
        .bind_protocol(BookProtocol) \
        .build()

    book: Book = client.get_book(1, "name")
