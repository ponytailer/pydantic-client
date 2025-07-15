"""
Example: Async API client with HttpxWebClient and Agno tools
"""
import asyncio
from pydantic import BaseModel
from pydantic_client import HttpxWebClient, get, post

class Product(BaseModel):
    id: int
    name: str
    price: float

class MyHttpxClient(HttpxWebClient):
    def __init__(self):
        super().__init__(base_url="https://api.example.com")

    @get("/products/{product_id}", agno_tool=True, tool_description="Get product info by ID")
    async def get_product(self, product_id: int) -> Product:
        """
        :param product_id: Product ID
        """
        ...

    @post("/products", agno_tool=True, tool_description="Create a new product")
    async def create_product(self, product: Product) -> Product:
        """
        :param product: Product object
        """
        ...

async def main():
    client = MyHttpxClient()
    # product = await client.get_product(101)
    # print("Product info:", product)
    class DummyAgent:
        def register_tool(self, name, description, parameters, call):
            print(f"Register tool: {name}, desc: {description}, params: {parameters}")
    agent = DummyAgent()
    client.register_agno_tools(agent)

if __name__ == "__main__":
    asyncio.run(main())
