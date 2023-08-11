import requests


class MockResponse:

    def __init__(self, code, response):
        self.code = code
        self.response = response

    @property
    def ok(self):
        return int(self.code) == 200

    def json(self):
        return self.response

    def raise_for_status(self):
        if not self.ok:
            raise

    @property
    def status_code(self):
        return self.code


def mock_requests(
    monkeypatch,
    response=None,
    code=200
):

    def mock_call(mock_return_value):
        def mock(*args, **kwargs):
            return MockResponse(**mock_return_value)

        return mock

    return_value = {"code": code, "response": response or {}}
    monkeypatch.setattr(
        requests.Session, "request",
        mock_call(return_value)
    )
