# modified from extreme4all's bot detector discord bot

import logging
import random

import re
import discord
from discord.ext import commands
from src.functions import get_url, post_url, check_match_id
from discord.ext.commands import Context, Cog
from discord import app_commands
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

    async def __validate_rsn(self, login: str) -> bool:
        login = login.strip()
        if re.fullmatch("[\w\d\s_-]{1,12}", login):
            return login
        return None

    @commands.command(name="poke")
    async def poke(self, ctx: Context):
        """Poke the server to determine latency"""
        debug = {
            "author": ctx.author.name,
            "author_id": ctx.author.id,
            "msg": "requested a poke",
        }
        logger.debug(debug)
        url = config.BASE
        ping = await self.__web_request(url)
        isServerUp = "🟢 Online" if ping is not None else "🔴 Offline"

        embed = discord.Embed(color=0x00FF)
        embed.add_field(name="Ping", value=f"{self.bot.latency:.3f} ms", inline=False)
        embed.add_field(name="Status", value=f"{isServerUp}", inline=False)
        await ctx.reply(embed=embed)
        pass

    @commands.command(name="whois")
    async def whois(self, ctx: Context, *login: str):
        """Finding the discord username of a player's RSN in-game."""
        login = " ".join(list(login))
        if not login:
            await ctx.reply("You must enter an RSN.")
        login = await self.__validate_rsn(login)
        if not login:
            await ctx.reply(f"{login} is not a valid RSN type.")
            return

        route = (
            config.BASE
            + f"V1/discord/whois?token={config.DISCORD_ROUTE_TOKEN}&login={login}"
        )
        response = await get_url(route=route)
        await ctx.reply(response)

    @commands.command(name="logs")
    async def logs(self, ctx: Context):
        """Tips on how to access your client.log file"""
        response = (
            "To find the `logs`, you can **do one of the following**:\n"
            + "- If your client failed to open, click the `Open logs folder` button.\n"
            + "- Open the screenshot directory by right-clicking 📷 `Camera button`, navigate 1 directory up, then open `logs` folder.\n"
            + "- Navigate to `%userprofile%\.runelite\logs` on **Windows** or `$HOME/.runelite/logs` on **Linux** and **macOS**.\n"
        )
        embed = discord.Embed(
            color=15844367, title="📝 Submitting your `client.log` file. 📝"
        )
        embed = embed.add_field(name="Finding your client.log file", value=response)
        await ctx.reply(embed=embed)

    @commands.command(name="report")
    async def report(self, ctx: Context):
        """Report another player, or an issue with your match."""
        embed = discord.Embed(color=10038562, title="Report another Player")
        embed.add_field(
            name="➡️ Submitting via Discord",
            value="To report another player, please visit our support channel <#992457386189144074> and `Submit A Concern`.",
            inline=False,
        )
        embed.add_field(
            name="➡️ Jagex Rule Broken",
            value="If an in-game rule has been broken, please report these players in-game.",
            inline=False,
        )
        embed.add_field(
            name="➡️ Scamming/Theft of Items",
            value="In addition to reporting a player in-game, please submit a runewatch case here: https://runewatch.com/",
            inline=False,
        )
        await ctx.reply(embed=embed)

    @commands.command(name="bug")
    async def bug(self, ctx: Context):
        """Report a bug, or an issue with your plugin."""
        embed = discord.Embed(color=10181046, title="Bug Report")
        embed.add_field(
            name="➡️ Submitting via Discord",
            value="To submit a bug, please visit our support channel <#992457386189144074> and click `Submit Bug Report`.",
            inline=False,
        )
        embed.add_field(
            name="➡️ Submitting via Github",
            value="You can also go to our github and submit an issue: https://github.com/NeverScapeAlone/never-scape-alone/issues",
            inline=False,
        )
        await ctx.reply(embed=embed)

    @commands.command(name="meow")
    async def meow(self, ctx: Context):
        """Send a random cat image."""
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
