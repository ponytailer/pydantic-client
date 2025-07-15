from pydantic import BaseModel
from pydantic_client.base import BaseWebClient
from pydantic_client.tools.agno import register_agno_tool


class User(BaseModel):
    id: int
    name: str
    email: str


class ExampleClient(BaseWebClient):

    @register_agno_tool("Get user info")
    def get_user(self, user_id: int) -> User:
        """
        :param user_id: User ID
        """
        return User(id=user_id, name="John", email="john@example.com")


if __name__ == "__main__":
    client = ExampleClient(base_url="http://api.example.com")
    user = client.get_user(1)
    print("User info:", user)
    # Register agno tool to a dummy agent
    class DummyAgent:
        def register_tool(self, name, description, parameters, call):
            print(f"Register tool: {name}, desc: {description}, params: {parameters}")
    agent = DummyAgent()
    client.register_agno_tools(agent)
