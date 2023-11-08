import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture
async def body_status():
    async def inner(url: str, params: dict = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                body = await response.json()
                status = response.status
                return body, status

    return inner
