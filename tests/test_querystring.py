import pytest
import warnings
from pydantic import BaseModel
from pydantic_client import get, RequestsWebClient


class User(BaseModel):
    id: str
    name: str


# ---- 模拟网络请求，不实际发 http ----
class DummyClient(RequestsWebClient):
    def __init__(self):
        super().__init__(base_url="http://example.com")
        self.last_request = None

    def _request(self, kwargs):
        self.last_request = kwargs
        # 简化返回
        return kwargs


# ----- 1. 测试 querystring 动态渲染 -----
def test_querystring_rendering_all_params():
    class MyClient(DummyClient):
        @get("/users?name={name}&age={age}")
        def get_user(self, name: str, age: int):
            ...

    client = MyClient()
    client.get_user("alice", 20)
    assert client.last_request.path == "/users"
    assert client.last_request.params == {"name": "alice", "age": 20}


def test_querystring_rendering_partial_params():
    class MyClient(DummyClient):
        @get("/users?name={name}&age={age}&address=pp")
        def get_user(self, name: str = None, age: int = None):
            ...

    client = MyClient()
    client.get_user(name="bob")
    assert client.last_request.path == "/users"
    assert client.last_request.params == {"name": "bob"}
    client.get_user(age=30)
    assert client.last_request.params == {"age": 30}
    client.get_user()
    assert client.last_request.params == {}


def test_querystring_rendering_with_path_and_query():
    class MyClient(DummyClient):
        @get("/users/{uid}?active={active}")
        def get_user(self, uid: str, active: bool = None):
            ...

    client = MyClient()
    client.get_user("u1", active=True)
    assert client.last_request.path == "/users/u1"
    assert client.last_request.params == {"active": True}
    client.get_user("u2")
    assert client.last_request.params == {}


# ----- 2. 测试 path参数缺失 warning -----
def test_path_param_missing_warns(monkeypatch):
    warnings_list = []
    monkeypatch.setattr(warnings, "warn", lambda msg: warnings_list.append(msg))

    class MyClient(DummyClient):
        @get("/users/{user_id}")
        def get_user(self):
            ...

    assert any("missing parameters" in str(w).lower() for w in warnings_list)


def test_path_param_partial_missing_warns(monkeypatch):
    warnings_list = []
    monkeypatch.setattr(warnings, "warn", lambda msg: warnings_list.append(msg))

    class MyClient(DummyClient):
        @get("/users/{uid}/{bar}")
        def foo(self, uid):
            ...

    assert any("{'bar'}" in str(w) for w in warnings_list)


def test_path_param_no_warning_when_all_present(monkeypatch):
    monkeypatch.setattr(warnings, "warn", lambda msg: pytest.fail("Shouldn't warn"))
    class MyClient(DummyClient):
        @get("/users/{x}/{y}")
        def foo(self, x, y):
            ...
    # 不应报 warning

# ----- 3. 边界情况 -----
def test_querystring_param_name_overlap_path():
    class MyClient(DummyClient):
        @get("/search/{keyword}?keyword={keyword}&page={page}")
        def search(self, keyword: str, page: int = 1):
            ...

    client = MyClient()
    client.search("foo", page=5)
    assert client.last_request.path == "/search/foo"
    assert client.last_request.params == {"keyword": "foo", "page": 5}


def test_querystring_with_various_types():
    class MyClient(DummyClient):
        @get("/items?intv={intv}&boolv={boolv}&nonev={nonev}")
        def get(self, intv: int = None, boolv: bool = None, nonev: str = None):
            ...

    client = MyClient()
    client.get(intv=2, boolv=True)
    assert client.last_request.params == {"intv": 2, "boolv": True}
    client.get()
    assert client.last_request.params == {}


def test_querystring_no_params():
    class MyClient(DummyClient):
        @get("/users")
        def list_users(self):
            ...
    client = MyClient()
    client.list_users()
    assert client.last_request.path == "/users"
    assert client.last_request.params == {}
