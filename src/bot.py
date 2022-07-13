import logging
import discord
from discord.ext import tasks
import config
import json
import time
from functions import get_url, post_url

logger = logging.getLogger(__name__)

client = discord.Client()


@client.event
async def on_ready():
    await client.get_channel(985750992891043890).send(
        f"{client.user} has connected to Discord!"
    )
    logger.info(f"{client.user} has connected to Discord!")
    manage_channels.start()


@client.event
async def on_connect():
    logger.info("Bot connected successfully.")


@client.event
async def on_disconnect():
    logger.info("Bot disconnected.")


@client.event
async def on_message(message):
    if message.author.id == config.TICKET_BOT:
        await ticket_parser(message=message)
        return

    if message.author == client.user:
        return


async def run_active_queues():
    queue_route = (
        config.BASE + f"V1/discord/get-active-queues?token={config.DISCORD_ROUTE_TOKEN}"
    )
    connections_route = config.BASE + f"V1/server-status/connections"

    response = await get_url(route=queue_route)
    connections = await get_url(route=connections_route)
    channel = client.get_channel(config.ACTIVE_QUEUES_CHANNEL)
    messages = await channel.history(limit=5).flatten()

    embed = discord.Embed(
        title="Active Queues", description=f"Updated: <t:{int(time.time())}:R>"
    )
    minute_connections = connections["minute_connections"]
    hour_connections = connections["hour_connections"]
    embed = embed.set_footer(
        text=f"Active Users: {minute_connections} | Past Hour: {hour_connections}"
    )

    if "detail" in response.keys():
        if response["detail"] == "bad token":
            logging.warning(response["detail"])
            return
        if response["detail"] == "no information":
            embed.add_field(name="Active Queues", value="None", inline=False)
    else:
        for activity in response:
            count = response[activity]
            embed.add_field(name=activity, value=count, inline=False)

    if len(messages) > 0:
        message = messages[0]
        await message.edit(embed=embed)
        return

    await channel.send(embed=embed)
    return


@tasks.loop(seconds=5)
async def manage_channels():
    await run_active_queues()

    route = (
        config.BASE
        + f"V1/discord/get-active-matches?token={config.DISCORD_ROUTE_TOKEN}"
    )

    response = await get_url(route=route)

    if "detail" in response.keys():
        logging.warning(response["detail"])
        return

    active_parties = response["parties"]
    matches = client.get_channel(config.MATCH_CATEGORY).channels
    match_names = [match.name for match in matches]

    if len(active_parties) > 0:
        for party, invite in active_parties:
            if party in match_names:
                continue
            await client.get_channel(config.MATCH_CATEGORY).create_voice_channel(party)

    if len(active_parties) == 0:
        for match in matches:
            await client.get_channel(match.id).delete(reason="Match No Longer Active.")
        return

    parties, invites = list(zip(*active_parties))
    party_invites = dict(zip(parties, invites))

    sub_payload = []
    for match in matches:
        temp_dict = dict()
        if match.name not in parties:
            await client.get_channel(match.id).delete(reason="Match No Longer Active.")
        else:
            if party_invites[match.name] == None:
                invite = await client.get_channel(match.id).create_invite(
                    max_age=1800,
                    max_uses=0,
                    unique=False,
                    reason="No previous invite created.",
                )
                temp_dict["party_identifier"] = match.name
                temp_dict["discord_invite"] = str(invite)
                sub_payload.append(temp_dict)

    if len(sub_payload) == 0:
        return
    payload = dict()
    payload["invite_pairs"] = sub_payload
    data = json.dumps(payload)
    route = config.BASE + f"V1/discord/post-invites?token={config.DISCORD_ROUTE_TOKEN}"
    await post_url(route=route, data=data)


async def ticket_parser(message):
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
                        await verification_parser(
                            channel=channel, discord=discord, login=login
                        )
                        return


async def verification_parser(channel, discord, login):
    if login is None and discord is None:
        return
    await channel.send(f"Verifying `{login}` for `{discord}`")

    url_safe_discord = str(discord).replace("#", "%23")
    append = f"V1/discord/verify?login={login}&discord={url_safe_discord}&token={config.DISCORD_ROUTE_TOKEN}"
    route = config.BASE + append

    response = await get_url(route)
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
    return


async def bad_rsn(channel, discord, login):
    await channel.send(
        "The RSN that you have entered is invalid. It does not match the regex pattern: [\w\d\s_-]{1,12}. Please make a new ticket to re-enter your RSN."
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
        + f"2. Entered your RSN EXACTLY as displayed in-game? This includes underscores where needed, spaces where needed, and capitalizations?\n"
        + f"Make sure that you do the following:\n"
        + f"1. Open your Plugin Configuration (Wrench Icon in the Top Right of RuneLite)\n"
        + f"2. Search 'NeverScapeAlone'\n"
        + f"3. Click the Gear in NeverScapeAlone (Edit Plugin Configuration)\n"
        + f"4. In the 'Discord Username' field, enter `{discord}`.\n"
        + f"5. Turn your Plugin OFF and then ON. (Disable and then Enable NeverScapeAlone).\n"
        + f"6. You should see 'SUCCESSFULLY REGISTERED'.\n"
        + f"7. Close this ticket.\n"
        + f"8. Make a new ticket with your RSN, as before.\n"
        + f"Note: If you continue to have issues verifying your account, double check that you've entered in your data correctly, try again, then contact support.\n"
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
    role = client.get_guild(config.GUILD_ID).get_role(992927728779153409)
    await discord.add_roles(role)


client.run(config.TOKEN)
