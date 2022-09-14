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


class eventCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the eventCommands class.
        :param bot: The discord bot client.
        """
        self.bot = bot

    @commands.command(name="random")
    @commands.has_role(config.EVENT_MODERATOR)
    async def random(self, ctx: Context, time_start: str):
        """[EVENT MODERATORS] create a random event"""

    @commands.command(name="start")
    @commands.has_role(config.EVENT_MODERATOR)
    async def start(self, ctx: Context, activity: str, time_start: str):
        """[EVENT MODERATORS] create an event"""
