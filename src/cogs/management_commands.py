# modified from extreme4all's bot detector discord bot

import json
import logging
from types import NoneType

import discord
import src.config as config
import src.models as models
from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord.app_commands import checks
from src.functions import check_match_id, get_url, post_url

logger = logging.getLogger(__name__)


class managementCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the managementCommands class.
        :param bot: The discord bot client.
        """
        self.bot = bot

    def __convert_url(self, url):
        url = url.replace("api.", "").replace("repos/", "")
        return url

    @commands.command(name="update")
    @checks.has_role(config.OWNER_ROLE)
    async def delete(self, ctx: Context):
        route = (
            config.BASE + f"V1/discord/update-api?token={config.DISCORD_ROUTE_TOKEN}"
        )
        response = await get_url(route=route)
        response = json.dumps(response)
        response = json.loads(response)
        embed = discord.Embed(
            color=2067276,
            title="API Update",
            description=response["detail"],
        )
        await ctx.reply(embed=embed)

    @commands.command(name="top10")
    @checks.has_role(config.OWNER_ROLE)
    async def delete(self, ctx: Context):
        route = config.BASE + f"V1/discord/get-tasks?token={config.DISCORD_ROUTE_TOKEN}"
        response = await get_url(route=route)
        response = json.dumps(response)
        response = json.loads(response)

        issue_list = response["issues"]
        embed = discord.Embed(
            color=2067276,
            title="Top 10 Issues Sorted by Development Priority",
        )

        for c, issue in enumerate(issue_list):
            title = issue["title"]
            url = self.__convert_url(url=issue["url"])
            priority = issue["priority"]
            embed = embed.add_field(
                name=f"#{c+1} § ({priority})",
                value=f"[{title}]({url})",
                inline=False,
            )
            if c == 9:
                break
        await ctx.reply(embed=embed)
