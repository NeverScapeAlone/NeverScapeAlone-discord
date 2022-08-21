# modified from extreme4all's bot detector discord bot

import json
import logging
from types import NoneType
import re

import discord
import src.config as config
import src.models as models
from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord.app_commands import checks
from src.functions import check_match_id, get_url, post_url

import codecs
import re

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

    def __slashescape(self, err):
        """codecs error handler. err is UnicodeDecode instance. return
        a tuple with a replacement for the unencodable part of the input
        and a position where encoding should continue"""
        # print err, dir(err), err.start, err.end, err.object[:err.start]
        thebyte = err.object[err.start : err.end]
        repl = "\\x" + hex(ord(thebyte))[2:]
        return (repl, err.end)

    def __parse_file(self, stream):
        codecs.register_error("slashescape", self.__slashescape)

        # --- processing

        lines = []
        for line in [stream]:
            lines.append(line.decode("utf-8", "slashescape"))

        file = lines[0]
        file = file.replace("\n", "")
        file = file.replace("\r", "")
        file = file.replace("\tat", "")
        file = re.sub(
            "[0-9]{4}-[0-9]{2}-[0-9]{2}[ ]{1}[0-9]{2}:[0-9]{2}:[0-9]{2}",
            "§SEPERATOR§",
            file,
        )
        lines = file.split("§SEPERATOR§")

        parsed = list()
        version = ""
        for line in lines:
            l = line.lower()
            if l.find("neverscapealone") != -1:
                if l.find("version") != -1:
                    version = (
                        line[
                            line.find("version") + len("version") : line.find("commit")
                        ]
                        .replace('"', "")
                        .strip()
                    )
                parsed.append(line.strip())
        return version, parsed

    @commands.command(name="update")
    @commands.has_role(config.OWNER_ROLE)
    async def update(self, ctx: Context):
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
    @commands.has_role(config.OWNER_ROLE)
    async def top10(self, ctx: Context):
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

    @commands.command(name="parse")
    @commands.has_any_role(config.MATCH_MODERATOR, config.OWNER_ROLE, config.STAFF)
    async def parse(self, ctx: Context):
        """quickly parses a client.log file"""
        # determine if the current !parse command is self, or in relation to a reply.
        attachments = []
        if ctx.message.reference.message_id:
            # check if interaction has the attachment
            message = await ctx.fetch_message(ctx.message.reference.message_id)
            attachments = message.attachments
        if ctx.message.attachments:
            # check if current has the attachment, prioritize this and override check
            attachments = ctx.message.attachments
        if not attachments:
            embed = discord.Embed(
                title="Please attach your client.log file, or reference an attached client.log file!"
            )
            await ctx.reply(embed=embed)
            return
        for attachment in attachments:
            if attachment.filename != "client.log":
                continue
            await ctx.typing()
            await ctx.reply(f"Processing {attachment.filename} file...")
            content = await attachment.read()
            if content:
                break

        await ctx.typing()
        version, parsed = self.__parse_file(stream=content)
        embed = discord.Embed(
            title=f"client.log Parsed", description=f"Plugin Version {version}"
        )
        for c, line in enumerate(parsed[2:]):
            embed.add_field(name=f"Line {c+1}", value=line, inline=False)
        await ctx.reply(embed=embed)
