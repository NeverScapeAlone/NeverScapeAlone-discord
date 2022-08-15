import aiohttp
import json
import re


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


async def check_match_id(match_id: str) -> bool:
    if re.fullmatch("^[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}", match_id):
        return True
    return False
