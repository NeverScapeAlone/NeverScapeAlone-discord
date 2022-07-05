import aiohttp
import json


async def get_url(route):
    async with aiohttp.ClientSession() as session:
        async with session.get(route) as resp:
            response = await resp.text()
    response = json.loads(response)
    return response


async def post_url(route, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=route, json=data) as resp:
            response = await resp.text()
