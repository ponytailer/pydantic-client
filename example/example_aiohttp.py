"""
Example: Async API client with AiohttpWebClient and Agno tools
"""
import asyncio
from pydantic import BaseModel
from pydantic_client import AiohttpWebClient, get, post

class Order(BaseModel):
    id: int
    item: str
    quantity: int

class MyAiohttpClient(AiohttpWebClient):
    def __init__(self):
        super().__init__(base_url="https://api.example.com")

    @get("/orders/{order_id}", agno_tool=True, tool_description="Get order info by ID")
    async def get_order(self, order_id: int) -> Order:
        """
        :param order_id: Order ID
        """
        ...

    @post("/orders", agno_tool=True, tool_description="Create a new order")
    async def create_order(self, order: Order) -> Order:
        """
        :param order: Order object
        """
        ...

async def main():
    client = MyAiohttpClient()
    # order = await client.get_order(555)
    # print("Order info:", order)
    class DummyAgent:
        def register_tool(self, name, description, parameters, call):
            print(f"Register tool: {name}, desc: {description}, params: {parameters}")
    agent = DummyAgent()
    client.register_agno_tools(agent)

if __name__ == "__main__":
    asyncio.run(main())
