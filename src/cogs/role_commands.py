# modified from extreme4all's bot detector discord bot

import logging
import datetime
import string

import discord
from src.activities import ActivityReference
import src.config as config
from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord.ui import View, Select

logger = logging.getLogger(__name__)


class roleCommands(Cog):
    def __init__(self, bot: discord.Client) -> None:
        """
        Initialize the roleCommands class.
        :param bot: The discord bot client.
        """
        self.bot = bot

    @commands.hybrid_command(name="add_role")
    async def add_role(self, ctx: Context, search: str):
        async def callback(interaction: discord.Interaction):
            roles = []
            for role_id in select.values:
                roles.append(interaction.guild.get_role(int(role_id)))
            await interaction.user.add_roles(*roles)
            role_names = ", ".join([role.name for role in roles])
            await interaction.response.send_message(
                f"Your roles have been added: {role_names}"
            )
            return

        if len(search) < 3:
            await ctx.reply(
                "You must enter in a longer role search string. Ex. `Attack`."
            )
            return

        a = ActivityReference()
        activities = a.activities
        search = search.upper()
        search = search[:3]

        search_items = []
        for c, t, p, i in activities:
            if search in p:
                search_items.append(p)

        if not search_items:
            await ctx.reply("No activities could be found. Please refine your search.")
            return

        if len(search_items) > 25:
            await ctx.reply(
                "There are over 25 selection options, your search could not be completed. Please refine your search."
            )
            return

        option_list = []
        for p in search_items:
            option_list.append(
                discord.SelectOption(label=a.pt_dict[p], value=a.pi_dict[p])
            )

        view = View()
        select = Select(min_values=1, max_values=len(option_list), options=option_list)
        select.callback = callback
        view.add_item(select)

        await ctx.send("Select an activity to be pinged on: ", view=view)

    @commands.hybrid_command(name="remove_role")
    async def remove_role(self, ctx: Context, search: str):
        async def callback(interaction: discord.Interaction):
            roles = []
            for role_id in select.values:
                roles.append(interaction.guild.get_role(int(role_id)))
            await interaction.user.remove_roles(*roles)
            role_names = ", ".join([role.name for role in roles])
            await interaction.response.send_message(
                f"Your roles have been removed: {role_names}"
            )
            return

        if len(search) < 3:
            await ctx.reply(
                "You must enter in a longer role search string. Ex. `Attack`."
            )
            return

        a = ActivityReference()
        activities = a.activities
        search = search.upper()
        search = search[:3]

        search_items = []
        for c, t, p, i in activities:
            if search in p:
                search_items.append(p)

        if not search_items:
            await ctx.reply("No activities could be found. Please refine your search.")
            return

        if len(search_items) > 25:
            await ctx.reply(
                "There are over 25 selection options, your search could not be completed. Please refine your search."
            )
            return

        option_list = []
        for p in search_items:
            option_list.append(
                discord.SelectOption(label=a.pt_dict[p], value=a.pi_dict[p])
            )

        view = View()
        select = Select(min_values=1, max_values=len(option_list), options=option_list)
        select.callback = callback
        view.add_item(select)

        await ctx.send("Select roles to be removed: ", view=view)
