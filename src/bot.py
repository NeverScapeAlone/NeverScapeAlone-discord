from dis import disco
import logging
import discord
import config
import aiohttp
import json

logger = logging.getLogger(__name__)

client = discord.Client()


@client.event
async def on_ready():
    await client.get_channel(985750992891043890).send(
        f"{client.user} has connected to Discord!"
    )
    logger.info(f"{client.user} has connected to Discord!")


@client.event
async def on_connect():
    logger.info("Bot connected successfully.")


@client.event
async def on_disconnect():
    logger.info("Bot disconnected.")


@client.event
async def on_message(message):
    if len(message.mentions) == 1:
        login = discord = None
        discord = message.mentions[0]
        channel = client.get_channel(message.channel.id)
        messages = await channel.history(limit=5).flatten()

        for msg in messages:
            embeds = msg.embeds
            if len(embeds) == 0:
                continue
            for embed in embeds:
                response = embed.to_dict()
                if "fields" not in response.keys():
                    continue
                for field in response["fields"]:
                    if field["name"] == "Post your RSN Here":
                        login = field["value"]

        if login is None and discord is None:
            return
        await channel.send(f"Verifying `{login}` for `{discord}`")

        base = f"http://127.0.0.1:8000/"
        if not config.DEV_MODE:
            base = f"https://touchgrass.online/"

        url_safe_discord = str(discord).replace("#", "%23")
        append = f"V1/discord/verify?login={login}&discord={url_safe_discord}&token={config.DISCORD_ROUTE_TOKEN}"
        route = base + append

        async with aiohttp.ClientSession() as session:
            async with session.get(route) as resp:
                response = await resp.text()

        response = json.loads(response)

        response = response["detail"]

        response_parser = {
            "bad rsn": bad_rsn,
            "bad discord": bad_discord,
            "bad token": bad_token,
            "no information": no_information,
            "contact support": contact_support,
            "already verified": already_verified,
            "verified": verified,
        }

        await response_parser[response](channel=channel, discord=discord, login=login)

    if message.author == client.user:
        return


async def bad_rsn(channel, discord, login):
    await channel.send(
        f"The RSN that you have entered is invalid. It does not match the regex pattern: [\w\d\s_-]{1,12}. Please make a new ticket to re-enter your RSN."
    )
    return


async def bad_discord(channel, discord, login):
    await channel.send(
        f"Your discord pattern is invalid. Support will be contacted, as they will need to check your logs. <@178965680266149888>"
    )
    return


async def bad_token(channel, discord, login):
    await channel.send(
        f"The token provided is invalid. This should not happen, unless you are running a bootleg version of the discord bot, or the server owners have not provided the correct key. <@178965680266149888>"
    )
    return


async def no_information(channel, discord, login):
    await channel.send(
        f"We do not have information regarding this account. Are you sure that you have:\n"
        + f"1. Entered your Discord in the format of `{discord}` in your plugin panel.\n"
        + f"2. Entered your RSN EXACTLY as displayed in-game? This includes underscores where needed, spaces where needed, and capitalizations?"
    )
    return


async def contact_support(channel, discord, login):
    await channel.send(
        f"Unfortunately, something went wrong on our end. Support has been alerted. <@178965680266149888>"
    )


async def already_verified(channel, discord, login):
    await channel.send(
        f"Your account has already been verified for {discord} and {login}. If you believe this to be in error, please contact support. Thank you!"
    )


async def verified(channel, discord, login):
    await channel.send(
        f"🎉  Your account has been verified! 🎉 \n"
        + "We hope that you enjoy the plugin. If you have any questions or concerns, please notify support. You are free to close the ticket."
    )


client.run(config.TOKEN)
