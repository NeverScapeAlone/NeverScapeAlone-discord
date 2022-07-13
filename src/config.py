import json
import logging
import os
import sys

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv(), verbose=True)

TOKEN = os.environ.get("discord_token")
DISCORD_ROUTE_TOKEN = os.environ.get("discord_route_token")
TICKET_BOT = 508391840525975553
GUILD_ID = 985750991846666284
MATCH_CATEGORY = 993321356005486592
ACTIVE_QUEUES_CHANNEL = 996565302202605619
# BASE = "http://127.0.0.1:8000/"
BASE = "http://touchgrass.online:5000/"

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
