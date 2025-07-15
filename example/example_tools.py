"""
Example: Registering multiple API endpoints as Agno tools
"""
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get, post

class MathResult(BaseModel):
    result: int

class ToolClient(RequestsWebClient):
    def __init__(self):
        super().__init__(base_url="https://api.example.com")

    @get("/add", agno_tool=True, tool_description="Add two numbers")
    def add(self, a: int, b: int) -> MathResult:
        """
        :param a: First number
        :param b: Second number
        """
        ...

    @post("/multiply", agno_tool=True, tool_description="Multiply two numbers")
    def multiply(self, a: int, b: int) -> MathResult:
        """
        :param a: First number
        :param b: Second number
        """
        ...

if __name__ == "__main__":
    client = ToolClient()
    # result = client.add(2, 3)
    # print("Add result:", result)
    class DummyAgent:
        def register_tool(self, name, description, parameters, call):
            print(f"Register tool: {name}, desc: {description}, params: {parameters}")
    agent = DummyAgent()
    client.register_agno_tools(agent)
