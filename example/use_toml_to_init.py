from example.protocol import BookProtocol, Book
from pydantic_client import PydanticClient
from pydantic_client.clients import RequestsClient

if __name__ == "__main__":
    client = PydanticClient.from_toml("config.toml") \
        .bind_client(RequestsClient) \
        .bind_protocol(BookProtocol) \
        .build()

    book: Book = client.get_book(1, "name")
