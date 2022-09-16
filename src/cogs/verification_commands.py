# modified from extreme4all's bot detector discord bot

import logging
import re
from types import NoneType

import discord
from discord.ext import commands
from discord.ext.commands import Context, Cog
import src.config as config
from src.functions import get_url, post_url, check_match_id

logger = logging.getLogger(__name__)


class verificationCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the verificationCommands class.
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

    async def __verification_parser(self, ctx, login):
        discord_id = ctx.author.id
        if login is None and discord_id is None:
            return

        append = f"V1/discord/verify?login={login}&discord_id={discord_id}&token={config.DISCORD_ROUTE_TOKEN}"
        route = config.BASE + append

        response = await get_url(route)
        response = response["detail"]

        response_parser = {
            "bad rsn": self.__bad_rsn,
            "bad discord": self.__bad_discord,
            "bad token": self.__bad_token,
            "no information": self.__no_information,
            "contact support": self.__contact_support,
            "already verified": self.__already_verified,
            "verified": self.__verified,
        }

        return await response_parser[response](ctx=ctx, login=login)

    async def __bad_rsn(self, ctx, login):
        response = "The RSN that you have entered is invalid. It does not match the regex pattern: [\w\d\s_-]{1,12}. Please re-enter your RSN."
        embed = discord.Embed(colour=16776960, title="❌Bad Rsn❌")
        embed = embed.add_field(name="Status", value=response)
        return embed

    async def __bad_discord(self, ctx, login):
        response = (
            f"Your discord pattern is invalid. Please visit <#992457386189144074>."
        )
        embed = discord.Embed(colour=15158332, title="❌Bad Discord❌")
        embed = embed.add_field(name="Status", value=response)
        return embed

    async def __bad_token(self, ctx, login):
        response = f"The token provided is invalid. This should not happen, unless you are running a bootleg version of the discord bot, or the server owners have not provided the correct key. <@178965680266149888>"
        embed = discord.Embed(colour=15158332, title="❌Bad Token❌")
        embed = embed.add_field(name="Status", value=response)
        return embed

    async def __no_information(self, ctx, login):
        embed = discord.Embed(colour=16776960, title="❓No Information❓")
        embed = embed.add_field(
            name="Status",
            value="We do not have information regarding this account. Follow these steps!\n __**MAKE SURE THAT YOU HAVE USED THE PLUGIN AT LEAST ONCE BEFORE VERIFYING!**__",
            inline=False,
        )
        embed = embed.add_field(name="➡️ Step 1", value="Log out and close RuneLite.")
        embed = embed.add_field(
            name="➡️ Step 2",
            value="Turn ON your discord desktop app, so that discord is running on your PC.",
            inline=False,
        )
        embed = embed.add_field(name="➡️ Step 3", value="Relaunch RuneLite.")
        embed = embed.add_field(
            name="➡️ Step 4",
            value="Go to the `Search` bar in the `NeverScapeAlone` plugin, type in `*` and press `Enter` on your keyboard.",
            inline=False,
        )
        embed = embed.add_field(
            name="➡️ Step 5",
            value="Even if no matches were found, your discord ID should have been sent to the server during this process.",
            inline=False,
        )
        embed = embed.add_field(
            name="➡️ Step 6",
            value="Enter your RSN EXACTLY as displayed in-game. This includes underscores where needed, spaces where needed, and capitalizations.",
            inline=False,
        )
        embed = embed.add_field(
            name="❗ Note",
            value="If you continue to have issues verifying your account, double check that you've entered in your data correctly, **LAUNCH RUNELITE IN ADMINISTRATOR MODE**, try again, then contact support.",
            inline=False,
        )
        embed = embed.add_field(
            name="❕ Other",
            value="If the issue still has not resolved. Please send your `client.log` file in the ticket. You can find this file by going to `.runelite > logs > client.log`.",
            inline=False,
        )
        return embed

    async def __contact_support(self, ctx, login):
        response = f"Unfortunately, something went wrong on our end. Please visit <#992457386189144074>"
        embed = discord.Embed(colour=15158332, title="💻Contact Support💻")
        embed = embed.add_field(name="Status", value=response)
        return embed

    async def __already_verified(self, ctx, login):
        response = f"Your account has already been verified for {ctx.author} and {login}. If you believe this to be in error, please contact support. \n Be sure to visit <#1011433062883659797>!"
        embed = discord.Embed(colour=3066993, title="🎉Already Verified!🎉")
        embed = embed.add_field(name="Status", value=response)

        role = ctx.guild.get_role(config.VERIFIED_ROLE)
        await ctx.author.add_roles(role)
        return embed

    async def __verified(self, ctx, login):

        response = (
            f"🎉  Your account has been verified! 🎉 \n"
            + "We hope that you enjoy the plugin. If you have any questions or concerns, please notify support. \n"
            + "Be sure to visit <#1011433062883659797>!"
        )
        embed = discord.Embed(colour=3066993, title="🎉Verified!🎉")
        embed = embed.add_field(name="Status", value=response)

        role = ctx.guild.get_role(config.VERIFIED_ROLE)
        await ctx.author.add_roles(role)
        return embed

    @commands.hybrid_command(name="verify")
    async def verify(self, ctx: Context, login: str):
        """verifies your account"""
        if ctx.channel.id != config.VERIFY_CHANNEL:
            await ctx.reply(
                f"❌ This is the wrong channel for this command. ❌\n"
                + f"Please click <#{config.VERIFY_CHANNEL}>"
            )
            return
        if not login:
            await ctx.reply(f"You must enter in an RSN.")
            return
        login = await self.__validate_rsn(login)
        if not login:
            await ctx.reply(f"{login} is not a valid RSN type.")
            return

        embed = await self.__verification_parser(ctx=ctx, login=login)
        await ctx.reply(embed=embed)
