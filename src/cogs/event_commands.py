# modified from extreme4all's bot detector discord bot

import logging
import datetime

import discord
import src.config as config
from discord.ext import commands
from discord.ext.commands import Cog, Context

logger = logging.getLogger(__name__)


class eventCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the eventCommands class.
        :param bot: The discord bot client.
        """
        self.bot = bot

    async def __announce_event_command(self, event_object):
        channel = self.bot.get_channel(config.EVENT_ANNOUNCEMENT_CHANNEL)
        await channel.send(f"<@{config.EVENTS_ROLE}>")
        await channel.send(event_object.url)

    @commands.hybrid_command(name="create_event")
    @commands.has_role(config.EVENT_MODERATOR)
    async def start(
        self,
        ctx: Context,
        event_name: str,
        description: str,
        location: str,
        friends_chat: str,
        start_time: int,
        end_time: int,
    ):
        """[EVENT MODERATORS] create an event"""
        start = datetime.datetime.fromtimestamp(start_time).astimezone()
        end = datetime.datetime.fromtimestamp(end_time).astimezone()
        event_object = await ctx.guild.create_scheduled_event(
            name=event_name,
            description=f"FC: {friends_chat} - " + description,
            location=location,
            start_time=start,
            end_time=end,
        )
        await ctx.reply(f"Check <#{config.EVENT_ANNOUNCEMENT_CHANNEL}> for the event!")
        await self.__announce_event_command(
            event_object=event_object,
        )
