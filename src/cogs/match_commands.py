# modified from extreme4all's bot detector discord bot

import json
import logging
import random
import re
import subprocess
import time
from types import NoneType
import time
import io

import discord
import src.config as config
import src.models as models
from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord.app_commands import checks
from src.functions import check_match_id, get_url, post_url, AttrDict

logger = logging.getLogger(__name__)


class matchCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the matchCommands class.
        :param bot: The discord bot client.
        """
        self.bot = bot

    @commands.command(name="delete")
    @commands.has_role(config.MATCH_MODERATOR)
    async def delete(self, ctx: Context, match_id: str = None):
        """[MATCH MODERATORS] delete a match"""
        if not match_id:
            await ctx.reply("Please enter a Match ID")
            return

        if not await check_match_id(match_id=match_id):
            await ctx.reply("Invalid Match ID format")
            return

        route = (
            config.BASE
            + f"V1/discord/delete-match?token={config.DISCORD_ROUTE_TOKEN}&match_id={match_id}"
        )
        response = await get_url(route=route)
        await ctx.reply(response)

    @commands.command(name="getallmatches")
    @commands.has_role(config.MATCH_MODERATOR)
    async def getallmatches(self, ctx: Context, compress=1):
        """[MATCH MODERATORS] Get all matches"""
        route = (
            config.BASE
            + f"V1/discord/get-all-matches?token={config.DISCORD_ROUTE_TOKEN}"
        )
        response = await get_url(route=route)
        if not compress:
            output = "\n".join(response)
        else:
            output = ", ".join(response)
        await ctx.reply(output)

    @commands.command(name="cleanup")
    @commands.has_role(config.MATCH_MODERATOR)
    async def cleanup(self, ctx: Context):
        """[MATCH MODERATORS] get matches to clean up"""
        all_matches_route = (
            config.BASE
            + f"V1/discord/get-all-matches?token={config.DISCORD_ROUTE_TOKEN}"
        )
        active_matches_route = (
            config.BASE
            + f"V1/discord/get-active-matches?token={config.DISCORD_ROUTE_TOKEN}"
        )

        managed_matches = await get_url(route=all_matches_route)
        active_matches = await get_url(route=active_matches_route)
        active_matches = json.dumps(active_matches)
        active_matches = json.loads(active_matches)
        active_matches = active_matches["active_matches_discord"]
        active_IDs = [am["ID"] for am in active_matches]

        headless = [ID for ID in active_IDs if ID not in managed_matches]
        ghost = [ID for ID in managed_matches if ID not in active_IDs if ID != "0"]
        reply = (
            "**HEADLESS**"
            + "\n*These matches can be* `!deleted` *and joined.*"
            + "\n".join(headless)
            + "\n"
            + "\n**GHOST**"
            + "\n*These matches have no data, and require an API restart to clear*"
            + "\n"
            + "\n".join(ghost)
        )
        await ctx.reply(reply)

    @commands.command(name="history")
    @commands.has_role(config.MATCH_MODERATOR)
    async def history(self, ctx: Context, match_id: str = None):
        """[MATCH MODERATORS] get the history of a match"""
        if not match_id:
            await ctx.reply("Please enter a Match ID")
            return

        if not await check_match_id(match_id=match_id):
            await ctx.reply("Invalid Match ID format")
            return

        route = (
            config.BASE
            + f"V2/match_history?match_identifier={match_id}&access_token={config.DISCORD_ROUTE_TOKEN}"
        )

        response = await get_url(route=route)

        try:
            detail = response["detail"]
            await ctx.reply(detail)
            return
        except:
            pass

        match_history = response["match_history"]
        lines = []
        for data in match_history:
            keys = data.keys()
            if "afk_cleanup" in keys:
                out = data["afk_cleanup"]
                middle = "afk"
            elif "disconnect" in keys:
                out = data["disconnect"]
                middle = "disconnect"
            elif "successful_join" in keys:
                out = data["successful_join"]
                middle = "join"
            else:
                out = None
            if not out:
                continue
            t = time.ctime(data["time"])
            line = f"""[{t}] - {middle} - {out}"""
            lines.append(line)

        output = "\n".join(lines)
        buf = io.BytesIO(output.encode())
        cur_time = time.strftime(f"%Y%m%d%H%M%S")
        f = discord.File(buf, filename=f"{match_id}-{cur_time}.txt")
        await ctx.reply(file=f)

    @commands.command(name="info")
    async def info(self, ctx: Context, match_id: str = None):
        """get the current information for a match"""
        if not match_id:
            await ctx.reply("Please enter a Match ID")
            return

        if not await check_match_id(match_id=match_id):
            await ctx.reply("Invalid Match ID format")
            return
        route = (
            config.BASE
            + f"V1/discord/get-match-information?token={config.DISCORD_ROUTE_TOKEN}&match_id={match_id}"
        )
        response = await get_url(route=route)
        if response == "This match does not exist.":
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
