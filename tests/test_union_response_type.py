from typing import Optional, Union

import requests_mock
from pydantic import BaseModel

from pydantic_client import RequestsWebClient, get
from pydantic_client.schema import RequestInfo


class User(BaseModel):
    id: str
    name: Optional[str] = None


class User2(BaseModel):
    id: str
    age: Optional[int] = None


def get_user_type_handler(request_info: RequestInfo):
    type = request_info.params["type"]
    print(type)
    if type == "A":
        return User
    elif type == "B":
        return User2
    else:
        return None


class TestClient(RequestsWebClient):

    @get("/users?type={type}", response_type_handler=get_user_type_handler)
    def get_user(self, type: str) -> Union[User, User2]:
        ...


def test_get_union():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users?type=A',
            json={"id": "123"}
        )

        client = TestClient(base_url="http://example.com")
        response = client.get_user("A")

        assert isinstance(response, User)
        assert response.id == "123"

        m.get(
            'http://example.com/users?type=B',
            json={"id": "123"}
        )
        response = client.get_user("B")
        assert isinstance(response, User2)
        assert response.id == "123"
