from pydantic_client.base import BaseWebClient, SpanContext
from pydantic_client.schema import RequestInfo
from pydantic_client.tools.agno import register_agno_tool


class DummyAgent:
    def __init__(self):
        self.tools = []

    def set_tools(self, tools):
        self.tools = tools


class TestClient(BaseWebClient):
    def _request(self, request_info):
        return request_info

    @register_agno_tool("desc")
    def tool_method(self, x: int) -> int:
        """
        :param x: int param
        """
        return x + 1


def test_span_context_logs(monkeypatch):
    logs = []
    monkeypatch.setattr('logging.Logger.info', lambda self, msg: logs.append(msg))
    class DummyClient:
        _statsd_client = None
    with SpanContext(DummyClient(), prefix="foo") as c:
        assert isinstance(c, DummyClient)
    assert any("span start" in letter for letter in logs)
    assert any("span end" in letter for letter in logs)


def test_before_request():
    client = TestClient(base_url="http://a")
    params = {"foo": 1}
    assert client.before_request(params) == params


def test_span_method():
    client = TestClient(base_url="http://a")
    ctx = client.span("bar")
    assert isinstance(ctx, SpanContext)


def test_dump_request_params_merges_headers():
    client = TestClient(base_url="http://a", headers={"A": "B"})
    req = RequestInfo(method="GET", path="/x", headers={"C": "D"})
    out = client.dump_request_params(req)
    assert out["headers"]["A"] == "B"
    assert out["headers"]["C"] == "D"
    assert out["url"] == "http://a/x"


def test_register_agno_tools_and_get_agno_tools():
    client = TestClient(base_url="http://a")
    agent = DummyAgent()
    client.register_agno_tools(agent)
    assert any(t["name"] == 'tool_method' for t in agent.tools)
    tools = TestClient.get_agno_tools()
    assert any(t['name'] == 'tool_method' for t in tools)
