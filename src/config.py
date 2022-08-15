import json
import logging
import os
import sys

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv(), verbose=True)

TOKEN = os.environ.get("discord_token")
DISCORD_ROUTE_TOKEN = os.environ.get("discord_route_token")
TICKET_BOT = 992456721341628429
MATCH_MODERATOR = 1008529540454305842
GUILD_ID = 985750991846666284
VERIFY_CHANNEL = 1008569322232348683
MATCH_CATEGORY = 993321356005486592
ACTIVE_QUEUES_CHANNEL = 996565302202605619
VERIFIED_ROLE = 992927728779153409
COMMAND_PREFIX = "!"
# BASE = "http://127.0.0.1:8000/"
BASE = "http://touchgrass.online:5500/"

# setup logging
file_handler = logging.FileHandler(filename="logs/error.log", mode="a")
stream_handler = logging.StreamHandler(sys.stdout)
# # log formatting
formatter = logging.Formatter(
    json.dumps(
        {
            "ts": "%(asctime)s",
            "name": "%(name)s",
            "function": "%(funcName)s",
            "level": "%(levelname)s",
            "msg": json.dumps("%(message)s"),
        }
    )
)


file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

handlers = [file_handler, stream_handler]

logging.basicConfig(level=logging.DEBUG, handlers=handlers)
