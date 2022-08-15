# modified from extreme4all's bot detector discord bot

import logging
import random
import subprocess

import discord
from discord.ext import commands
from discord.ext.commands import Context, Cog
import src.config as config

logger = logging.getLogger(__name__)


class utilCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the utilCommands class.
        :param bot: The discord bot client.
        """
        self.bot = bot

    async def __web_request(self, url: str) -> dict:
        """
        Make a web request to the specified url.

        :param url: The url to make the request to.
        :return: The response from the request.
        """
        async with self.bot.Session.get(url) as response:
            if response.status != 200:
                logger.error({"status": response.status, "url": url})
                return None
            return await response.json()

    @commands.command(name="poke")
    async def poke(self, ctx: Context):
        debug = {
            "author": ctx.author.name,
            "author_id": ctx.author.id,
            "msg": "requested a poke",
        }
        logger.debug(debug)
        url = config.BASE
        ping = await self.__web_request(url)
        isServerUp = "Online" if ping is not None else "Uh-Oh"

        embed = discord.Embed(color=0x00FF)
        embed.add_field(
            name="Discord Ping:", value=f"{self.bot.latency:.3f} ms", inline=False
        )
        embed.add_field(
            name="NeverScapeAlone API status:", value=f"{isServerUp}", inline=False
        )
        await ctx.reply(embed=embed)
        pass

    @commands.command(name="meow")
    async def meow(self, ctx: Context):
        """
        Send a random cat image.
        """
        debug = {
            "author": ctx.author.name,
            "author_id": ctx.author.id,
            "msg": "requested a cat",
        }
        logger.debug(debug)
        if random.randint(0, 1) > 0:
            url = "https://cataas.com/cat/gif?json=true"
        else:
            url = "https://cataas.com/cat?json=true"

        data = await self.__web_request(url)
        if data is None:
            await ctx.reply("Ouw souwce fo' cats am cuwwentwy down, sowwy :3")
        else:
            await ctx.reply("https://cataas.com" + data["url"])
        return
