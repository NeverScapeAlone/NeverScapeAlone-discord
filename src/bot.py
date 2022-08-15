import json
import logging
import time
from typing import List, Optional, Text

import aiohttp
import discord
from discord.app_commands import checks, commands, tree
from discord.ext import tasks
from discord.ext.commands import Bot
from pydantic import BaseModel

import src.models as models
from src import config
from src.functions import get_url, post_url, check_match_id
from src.cogs.util_commands import utilCommands
from src.cogs.verification_commands import verificationCommands
from src.cogs.match_commands import matchCommands

logger = logging.getLogger(__name__)

activity = discord.Game("Old School RuneScape", type=discord.ActivityType.watching)
allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
intents = discord.Intents(
    messages=True, guilds=True, members=True, reactions=True, message_content=True
)


bot: discord.Client = Bot(
    allowed_mentions=allowed_mentions,
    command_prefix=config.COMMAND_PREFIX,
    description="Matching Players!",
    case_insensitive=True,
    activity=activity,
    intents=intents,
)


@bot.event
async def on_ready():
    logger.info(f"We have logged in as {bot.user}")
    bot.Session = aiohttp.ClientSession()
    await bot.add_cog(utilCommands(bot))
    await bot.add_cog(verificationCommands(bot))
    await bot.add_cog(matchCommands(bot))
    # run_queues.start()
    # manage_channels.start()


@bot.event
async def on_connect():
    logger.info("Bot connected successfully.")
    logger.info(f"{config.COMMAND_PREFIX=}")


@bot.event
async def on_disconnect():
    logger.info("Bot disconnected.")


@tasks.loop(seconds=20)
async def run_queues():
    queue_route = (
        config.BASE + f"V1/discord/get-active-queues?token={config.DISCORD_ROUTE_TOKEN}"
    )

    response = await get_url(route=queue_route)
    if response is None:
        return

    channel = bot.get_channel(config.ACTIVE_QUEUES_CHANNEL)
    message_iterator = channel.history(limit=5)
    messages = []
    async for message in message_iterator:
        messages.append(message)

    embed = discord.Embed(
        title="Public Matches", description=f"Updated: <t:{int(time.time())}:R>"
    )
    if "detail" in response.keys():
        if response["detail"] == "bad token":
            logging.warning(response["detail"])
            return
        if response["detail"] == "no information":
            embed.add_field(name="Public Matches", value="None", inline=False)
    else:
        for activity in response:
            count = response[activity]
            activity = activity.replace("_", " ").title()
            embed.add_field(name=activity, value=count, inline=False)

    if len(messages) > 0:
        message = messages[0]
        await message.edit(embed=embed)
        return

    await channel.send(embed=embed)
    return


@tasks.loop(seconds=10)
async def manage_channels():
    matches = bot.get_channel(config.MATCH_CATEGORY).channels
    match_names = [match.name for match in matches]

    route = (
        config.BASE
        + f"V1/discord/get-active-matches?token={config.DISCORD_ROUTE_TOKEN}"
    )

    response = await get_url(route=route)
    response = json.dumps(response)
    response = json.loads(response)
    response = response["active_matches_discord"]

    if not response:
        for match in matches:
            await bot.get_channel(match.id).delete(reason="Match No Longer Active.")
        return

    active_matches = [
        models.active_match_discord.parse_obj(active_match) for active_match in response
    ]

    if active_matches:
        for active_match in active_matches:
            party = active_match.ID
            if party in match_names:
                continue
            await bot.get_channel(config.MATCH_CATEGORY).create_voice_channel(party)
    else:
        for match in matches:
            await bot.get_channel(match.id).delete(reason="Match No Longer Active.")
        return

    parties = [active_match.ID for active_match in active_matches]
    invites = [active_match.discord_invite for active_match in active_matches]
    party_invites = dict(zip(parties, invites))

    sub_payload = []
    for match in matches:
        temp_dict = dict()
        if match.name not in parties:
            await bot.get_channel(match.id).delete(reason="Match No Longer Active.")
        else:
            if party_invites[match.name] == None:
                invite = await bot.get_channel(match.id).create_invite(
                    max_age=21600,
                    max_uses=0,
                    unique=False,
                    reason="No previous invite created.",
                )
                temp_dict["ID"] = match.name
                temp_dict["discord_invite"] = str(invite)
                sub_payload.append(temp_dict)

    if not sub_payload:
        return
    payload = dict()
    payload["invites"] = sub_payload
    data = json.dumps(payload)
    route = config.BASE + f"V1/discord/post-invites?token={config.DISCORD_ROUTE_TOKEN}"
    await post_url(route=route, data=data)
