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


class matchCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the matchCommands class.
        :param bot: The discord bot client.
        """
        self.bot = bot

    @commands.command(name="delete")
    @checks.has_role(config.MATCH_MODERATOR)
    async def delete(self, ctx: Context, match_id: str = None):
        if not await check_match_id(match_id=match_id):
            await ctx.reply("Invalid Match ID format")
            return

        route = (
            config.BASE
            + f"V1/discord/delete-match?token={config.DISCORD_ROUTE_TOKEN}&match_id={match_id}"
        )
        response = await get_url(route=route)
        await ctx.reply(response)

    @commands.command(name="info")
    async def info(self, ctx: Context, match_id: str = None):
        if not await check_match_id(match_id=match_id):
            await ctx.reply("Invalid Match ID format")
            return
        route = (
            config.BASE
            + f"V1/discord/get-match-information?token={config.DISCORD_ROUTE_TOKEN}&match_id={match_id}"
        )
        response = await get_url(route=route)
        if response == "This match does not exist":
            await ctx.reply(response)

        response = json.dumps(response)
        response = json.loads(response)
        m = models.match.parse_obj(response)
        embed = discord.Embed(
            title=f"{m.activity} - {m.ID}",
            description=f"Pulled <t:{int(time.time())}:R>",
        )

        names = ", ".join([player.login for player in m.players])
        embed.add_field(name="Private", value=m.isPrivate)
        embed.add_field(name="Players", value=f"{len(m.players)}/{m.party_members}")
        embed.add_field(name="Experience", value=f"{m.requirement.experience}")
        embed.add_field(name="Accounts", value=f"{m.requirement.accounts}")
        embed.add_field(name="Split Type", value=f"{m.requirement.split_type}")
        embed.add_field(name="Regions", value=f"{m.requirement.regions}")
        if m.ban_list:
            embed.add_field(name="Ban List", value=f"{m.ban_list}")
        embed.add_field(name="Players", value=f"{names}")
        if m.notes:
            embed.add_field(name="Notes", value=f"{m.notes}")
        if m.discord_invite:
            embed.add_field(name="Invite", value=f"{m.discord_invite}")
        await ctx.reply(embed=embed)
