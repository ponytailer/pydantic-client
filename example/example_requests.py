"""
Example: Synchronous API client with RequestsWebClient and Agno tools
"""
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get, post

class User(BaseModel):
    id: int
    name: str
    email: str

class MyAPIClient(RequestsWebClient):
    def __init__(self):
        super().__init__(base_url="https://api.example.com")

    @get("/users/{user_id}", agno_tool=True, tool_description="Get user info by ID")
    def get_user(self, user_id: int) -> User:
        """
        :param user_id: User ID
        """
        ...

    @post("/users", agno_tool=True, tool_description="Create a new user")
    def create_user(self, user: User) -> User:
        """
        :param user: User object
        """
        ...

if __name__ == "__main__":
    client = MyAPIClient()
    # Call as normal API
    # user = client.get_user(1)
    # print("User info:", user)
    # Register as agno tools
    class DummyAgent:
        def register_tool(self, name, description, parameters, call):
            print(f"Register tool: {name}, desc: {description}, params: {parameters}")
    agent = DummyAgent()
    client.register_agno_tools(agent)
