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
    if re.fullmatch("^[a-z]{3,7}-[a-z]{3,7}-[a-z]{3,7}", match_id):
        return True
    return False


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
