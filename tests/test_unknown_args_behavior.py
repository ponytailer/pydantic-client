import json

import requests_mock
from pydantic import BaseModel

from pydantic_client import RequestsWebClient, get, post
from pydantic_client.base import PydanticClientValidationError


class User(BaseModel):
    id: int = 1
    name: str = 'Mark'

class DataResponce(BaseModel):
    qs_static: str
    qs_dynamic: str

class TestClient(RequestsWebClient):
    @get('/{path_param}_request?qs_static=static_data&qs_dynamic={qs_dynamic}')
    def base_get_request(self, path_param, qs_dynamic) -> DataResponce: ...

    @get('/{path_param}_request?qs_static=static_data&qs_dynamic={qs_dynamic}')
    def base_get_qs_default_request(self, path_param, qs_dynamic: str = 'def-data') -> DataResponce: ...

    @post('/{path_param}_request?qs_static=static_data&qs_dynamic={qs_dynamic}')
    def base_post_request(self, path_param, body_data: User, qs_dynamic: str = 'def-data') -> DataResponce: ...

    @post('/post_unknown_args_query', unknown_args_behavior='query')
    def post_unknown_args_query(self, name: str, email: str) -> str: ...

    @post('/post_unknown_args_miss?name={name_aaaa}', unknown_args_behavior='not_allow')
    def post_unknown_args_miss(self, name: str) -> str: ...

    @post('/post_unknown_args_not_allow', unknown_args_behavior='not_allow')
    def post_unknown_args_not_allow(self, name: str, email: str) -> str: ...

    @post('/post_twice_body')
    def post_twice_body(self, name: str, email: str, user: User) -> str: ...

    @post('/post_twice_body_models')
    def post_twice_body_models(self, user: User, user2: User) -> str: ...

    @get('/get_request_with_body')
    def get_request_with_body(self, user: User) -> str: ...


def test_base_get_args():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/base_get_request',
            json={'qs_static': 'static_data', 'qs_dynamic': 'some-data'}
        )

        client = TestClient(base_url="http://example.com")
        client.base_get_request(path_param='base_get', qs_dynamic='some-data')

        assert m.called
        assert m.last_request.qs == {'qs_static': ['static_data'], 'qs_dynamic': ['some-data']}

def test_base_get_args_with_qs_default():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/base_get_qs_default_request',
            json={'qs_static': 'static_data', 'qs_dynamic': 'some-data'}
        )

        client = TestClient(base_url="http://example.com")
        client.base_get_qs_default_request(path_param='base_get_qs_default')

        assert m.called
        assert m.last_request.qs == {'qs_static': ['static_data'], 'qs_dynamic': ['def-data']}

def test_base_post_args():
    with requests_mock.Mocker() as m:
        m.post(
            'http://example.com/base_post_request',
            json={'qs_static': 'static_data', 'qs_dynamic': 'some-data'}
        )

        client = TestClient(base_url="http://example.com")
        client.base_post_request('base_post', User(id=2, name='Mark'))

        assert m.called
        assert m.last_request.qs == {'qs_static': ['static_data'], 'qs_dynamic': ['def-data']}
        assert json.loads(m.last_request.text) == {'id': 2, 'name': 'Mark'}

def test_unknown_args():
    with requests_mock.Mocker() as m:
        m.post(
            'http://example.com/post_unknown_args_query',
            json='{}'
        )

        client = TestClient(base_url="http://example.com")
        client.post_unknown_args_query(name='mark', email='example@example.com')

        assert m.called
        assert m.last_request.qs == {'name': ['mark'], 'email': ['example@example.com']}

    with requests_mock.Mocker() as m:
        m.post(
            'http://example.com/post_unknown_args_miss',
            json='{}'
        )

        client = TestClient(base_url="http://example.com")

        try:
            client.post_unknown_args_miss(name='mark')
            assert False, 'must be exception PydanticClientValidationError: Some arguments is not filled, verify path and func argument names'
        except PydanticClientValidationError:
            pass

    with requests_mock.Mocker() as m:
        m.post(
            'http://example.com/post_unknown_args_not_allow',
            json='{}'
        )

        client = TestClient(base_url="http://example.com")

        try:
            client.post_unknown_args_not_allow(name='mark', email='example@example.com')
            assert False, 'must be exception PydanticClientValidationError: Some arguments is not filled, verify path and func argument names'
        except PydanticClientValidationError:
            pass

def test_post_body_twice():
    client = TestClient(base_url="https://example.com")

    mock_data = [
        {
            "name": "post_twice_body",
            "output": ''
        },
        {
            "name": "post_twice_body_models",
            "output": ''
        },
        {
            "name": "get_request_with_body",
            "output": ''
        },
    ]

    client.set_mock_config(mock_config=mock_data)

    try:
        client.post_twice_body('mark', 'example@example.com', user=User(id=1, name='mark'))
        assert False, 'must be exception PydanticClientValidationError: Cannot fill body because is not empty'
    except PydanticClientValidationError:
        pass

    try:
        client.post_twice_body_models(User(id=1, name='mark'), User(id=2, name='mark'))
        assert False, 'must be exception PydanticClientValidationError: Cannot fill body because is not empty'
    except PydanticClientValidationError:
        pass

    try:
        client.get_request_with_body(User(id=1, name='mark'))
        assert False, 'must be exception PydanticClientValidationError: Cannot put body data in {method} request'
    except PydanticClientValidationError:
        pass
