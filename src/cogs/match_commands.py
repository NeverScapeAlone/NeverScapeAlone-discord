# modified from extreme4all's bot detector discord bot

from ast import Expression
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

    async def __log_command(self, author_login, command, group_id=None):
        channel = self.bot.get_channel(config.MODERATOR_LOGS)
        current_time = int(time.time())
        embed = discord.Embed(
            colour=1752220,
            title=f"{author_login} ran {command} {group_id} <t:{current_time}:R>",
        )
        await channel.send(embed=embed)

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
        await self.__log_command(
            author_login=ctx.author.display_name, command="!delete", group_id=match_id
        )
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
        await self.__log_command(
            author_login=ctx.author.display_name,
            command="!getallmatches",
            group_id=None,
        )
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
            + "\n"
            + "\n".join(headless)
            + "\n"
            + "\n**GHOST**"
            + "\n*These matches have no data, and require an API restart to clear*"
            + "\n"
            + "\n".join(ghost)
        )
        await self.__log_command(
            author_login=ctx.author.display_name, command="!cleanup", group_id=None
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
            elif "match_settings" in keys:
                match_settings = data["match_settings"]
                match_identifier = match_settings["match_id"]
                activity = match_settings["activity"]
                max_players = match_settings["max_players"]
                is_private = match_settings["is_private"]
                notes = match_settings["notes"]
                match_version = match_settings["match_version"]
                experience = match_settings["experience"]
                split_type = match_settings["split_type"]
                account_types = match_settings["account_types"]
                regions = match_settings["regions"]
                out = f"\n{match_version=}\n{match_identifier=} {activity=} {is_private=}\n{max_players=} {experience=} {split_type=}\n{account_types=} {regions=}\n{notes=}"
                middle = "match_creation"
            elif "disconnect" in keys:
                out = data["disconnect"]
                middle = "disconnect"
            elif "successful_join" in keys:
                out = data["successful_join"]
                middle = "join"
            elif "check_connection_request" in keys:
                out = data["check_connection_request"]
                middle = "connection_request"
            elif "location" in keys:
                location_payload = data["location"]
                location_information = location_payload["location_information"]
                x = location_information["x"]
                y = location_information["y"]
                regionX = location_information["regionX"]
                regionY = location_information["regionY"]
                regionID = location_information["regionID"]
                plane = location_information["plane"]
                world = location_information["world"]
                login = location_payload["login"]
                out = f"{login} @ {regionID=}, {world=}"
                middle = "location"
            elif "promote_request" in keys:
                promote_request = data["promote_request"]
                submitting_player = promote_request["submitting_player"]
                subject_player = promote_request["subject_player"]
                out = f"{submitting_player} wants to promote {subject_player}"
                middle = "promote_request"
            elif "promoted" in keys:
                promoted = data["promoted"]
                submitting_player = promoted["submitting_player"]
                subject_player = promoted["subject_player"]
                out = f"{submitting_player} promoted {subject_player}"
                middle = "promotion"
            elif "kick_request" in keys:
                kick_request = data["kick_request"]
                submitting_player = kick_request["submitting_player"]
                subject_player = kick_request["subject_player"]
                out = f"{submitting_player} wants to kick {subject_player}"
                middle = "kick_request"
            elif "kicked" in keys:
                kicked = data["kicked"]
                submitting_player = kicked["submitting_player"]
                subject_player = kicked["subject_player"]
                out = f"{submitting_player} kicked {subject_player}"
                middle = "kicked"
            elif "forceful_socket_disconnect" in keys:
                forceful_socket_disconnect = data["forceful_socket_disconnect"]
                player = forceful_socket_disconnect["login"]
                out = f"{player}"
                middle = "forceful_socket_disconnect"
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

        await self.__log_command(
            author_login=ctx.author.display_name, command="!history", group_id=match_id
        )
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
