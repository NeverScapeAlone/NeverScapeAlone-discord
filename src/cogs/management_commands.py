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

    def __parse_file(self, stream, verbose=False):
        codecs.register_error("slashescape", self.__slashescape)

        # --- processing

        lines = []
        for line in [stream]:
            lines.append(line.decode("utf-8", "slashescape"))

        file = lines[0]
        file = file.replace("\n", "")
        file = file.replace("\r", "")
        file = file.replace("\t", "")
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
            if l.find("neverscapealone") == -1:
                continue
            if l.find("version") != -1:
                version = (
                    line[line.find("version") + len("version") : line.find("commit")]
                    .replace('"', "")
                    .strip()
                )

            short = line[line.find("]") + len("]") :].strip()
            title = short[: short.find("-")].strip()
            description = short[short.find("-") + 1 :].strip()
            if not verbose:
                if title.find("NeverScapeAlonePlugin") != -1:
                    continue
                if title.find("ExternalPluginManager") != -1:
                    continue
            parsed.append((title, description))
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
            title="🎊 __Top 10 Issues Sorted by Development Priority__ 🎊",
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
    async def parse(self, ctx: Context, verbose=False):
        """quickly parses a client.log file"""
        # determine if the current !parse command is self, or in relation to a reply.
        attachments = []
        if ctx.message.reference:
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
            if attachment.filename.find("client") == -1:
                continue
            await ctx.typing()
            await ctx.reply(f"Processing {attachment.filename} file...")
            content = await attachment.read()
            if content:
                break
            else:
                embed = discord.Embed(title=f"Empty {attachment.filename}")
                await ctx.reply(embed=embed)
                return

        await ctx.typing()
        version, parsed = self.__parse_file(stream=content, verbose=verbose)
        embed = discord.Embed(
            title=f"📝 Parsed {attachment.filename} 📝",
            description=f"💽 Plugin Version {version} 💽",
        )

        if not parsed:
            embed.add_field(
                name=f"No Errors",
                value="There were no errors found for NeverScapeAlone.",
                inline=False,
            )
            await ctx.reply(embed=embed)
            return

        for title, description in parsed:
            embed.add_field(name=title, value=description, inline=False)
        try:
            await ctx.reply(embed=embed)
        except discord.errors.HTTPException:
            try:
                embed = discord.Embed(
                    title=f"📝 Parsed {attachment.filename} 📝",
                    description=f"💽 Plugin Version {version} 💽",
                )

                titles = []
                for title, description in parsed:
                    titles.append(title)
                titles = list(set(titles))
                for title in titles:
                    embed.add_field(name=title, value="\u200b", inline=False)
                await ctx.reply(embed=embed)
            except discord.errors.HTTPException:
                embed = discord.Embed(
                    title=f"📝 Unparsed {attachment.filename} 📝",
                    description=f"💽 Plugin Version {version} 💽",
                )
                embed.add_field(
                    name="File could not be parsed.",
                    value="Errors exceed 6000 characters.",
                )
                await ctx.reply(embed=embed)
