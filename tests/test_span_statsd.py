import time

from pydantic_client import RequestsWebClient


def test_span_statsd(monkeypatch):
    class DummyStatsd:
        def __init__(self):
            self.called = False
            self.last_value = None
        def timing(self, key, value):
            self.called = True
            self.last_value = (key, value)

    dummy = DummyStatsd()
    monkeypatch.setattr("statsd.StatsClient", lambda host, port: dummy)
    client = RequestsWebClient(base_url="http://x", statsd_address="localhost:8125")
    
    with client.span("testapi"):
        time.sleep(0.001)

    assert dummy.called
    assert dummy.last_value[0] == "testapi.elapsed"