# modified from extreme4all's bot detector discord bot

import logging
import random
import subprocess
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
        response = "The RSN that you have entered is invalid. It does not match the regex pattern: [\w\d\s_-]{1,12}. Please make a new ticket to re-enter your RSN."
        return response

    async def __bad_discord(self, ctx, login):
        response = f"Your discord pattern is invalid. Support will be contacted, as they will need to check your logs. <@178965680266149888>"
        return response

    async def __bad_token(self, ctx, login):
        response = f"The token provided is invalid. This should not happen, unless you are running a bootleg version of the discord bot, or the server owners have not provided the correct key. <@178965680266149888>"
        return response

    async def __no_information(self, ctx, login):
        response = (
            f"We do not have information regarding this account. Follow these steps!\n"
            + f"1. Log out and close RuneLite.\n"
            + f"2. Turn ON your discord desktop app, so that discord is running on your PC.\n"
            + f"3. Relaunch RuneLite.\n"
            + f"4. Go to the `Search` bar, type in `*` and press `Enter` on your keyboard.\n"
            + f"5. Even if no matches were found, your discord ID should have been sent to the server during this process.\n"
            + f"6. Close this ticket.\n"
            + f"7. Create a new Verify Account ticket.\n"
            + f"8. Enter your RSN EXACTLY as displayed in-game. This includes underscores where needed, spaces where needed, and capitalizations.\n"
            + f"Note: If you continue to have issues verifying your account, double check that you've entered in your data correctly, try again, then contact support.\n"
            + f"\n"
            + f"If the issue still has not resolved. Please send your `client.log` file in the ticket. You can find this file by going to `.runelite > logs > client.log`."
        )
        return response

    async def __contact_support(self, ctx, login):
        response = f"Unfortunately, something went wrong on our end. Support has been alerted. <@178965680266149888>"
        return response

    async def __already_verified(self, ctx, login):
        response = f"Your account has already been verified for {ctx.author} and {login}. If you believe this to be in error, please contact support. Thank you!"
        role = ctx.guild.get_role(config.VERIFIED_ROLE)
        await ctx.author.add_roles(role)
        return response

    async def __verified(self, ctx, login):
        response = (
            f"🎉  Your account has been verified! 🎉 \n"
            + "We hope that you enjoy the plugin. If you have any questions or concerns, please notify support. You are free to close the ticket."
        )
        role = ctx.guild.get_role(config.VERIFIED_ROLE)
        await ctx.author.add_roles(role)
        return response

    @commands.command(name="verify")
    async def verify(self, ctx: Context, login: str = None):
        if ctx.channel.id != config.VERIFY_CHANNEL:
            await ctx.reply(
                f"This is the wrong channel for this command. Please click <#{config.VERIFY_CHANNEL}>"
            )
            return
        if not login:
            await ctx.reply(f"You must enter in an RSN.")
            return
        login = await self.__validate_rsn(login)
        if not login:
            await ctx.reply(f"{login} is not a valid RSN type.")
            return

        response = await self.__verification_parser(ctx=ctx, login=login)
        await ctx.reply(response)
