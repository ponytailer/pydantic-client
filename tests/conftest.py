import asyncio
from typing import AsyncGenerator, Generator

import aiohttp
import pytest
from aiohttp import web


# Mock Server Routes
async def hello(request):
    return web.json_response({"message": "Hello, World!"})


async def echo_params(request):
    return web.json_response(dict(request.query))


async def echo_json(request):
    data = await request.json()
    return web.json_response(data)


async def user_by_id(request):
    user_id = request.match_info['user_id']
    return web.json_response({
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })


async def list_users(request):
    return web.json_response({"users": []})


async def get_user_string(request):
    return web.Response(text="abc")


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_server(aiohttp_client) -> AsyncGenerator[
    aiohttp.ClientSession, None]:
    app = web.Application()
    app.router.add_get('/hello', hello)
    app.router.add_get('/echo', echo_params)
    app.router.add_post('/echo', echo_json)
    app.router.add_get('/users/{user_id}', user_by_id)
    app.router.add_get('/users', list_users)
    app.router.add_post('/users/string', get_user_string)
    app.router.add_post('/users/bytes', get_user_string)
    app.router.add_post('/users/dict', list_users)

    client = await aiohttp_client(app)
    yield client
    await client.close()


@pytest.fixture
def base_url(mock_server) -> str:
    return str(
        mock_server.server.scheme + '://' + mock_server.server.host + ':' + str(
            mock_server.server.port))
