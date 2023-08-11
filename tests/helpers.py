import asyncio

import aiohttp
import httpx
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


class MockAsyncResponse(MockResponse):
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        ...

    @property
    def status(self):
        return self.code

    @property
    def is_success(self):
        return True


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


def mock_aio_http(
    monkeypatch,
    response=None,
    code=200
):

    def mock_call(mock_return_value):
        def mock(*args, **kwargs):
            return MockAsyncResponse(**mock_return_value)

        return mock

    return_value = {"code": code, "response": response or {}}
    monkeypatch.setattr(
        aiohttp.ClientSession, "request",
        mock_call(return_value)
    )


def mock_httpx(
    monkeypatch,
    response=None,
    code=200
):

    def mock_call(mock_return_value):
        async def mock(*args, **kwargs):
            await asyncio.sleep(0.1)
            return MockAsyncResponse(**mock_return_value)

        return mock

    return_value = {"code": code, "response": response or {}}
    monkeypatch.setattr(
        httpx.AsyncClient, "request",
        mock_call(return_value)
    )
