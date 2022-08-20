# modified from extreme4all's bot detector discord bot

import json
import logging
import random
import re
import subprocess
import time
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
