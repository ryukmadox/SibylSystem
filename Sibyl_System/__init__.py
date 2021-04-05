"""Gets ENV vars or Config vars then calls class."""

from telethon import events
from telethon.sessions import StringSession
from motor import motor_asyncio
import aiohttp
import json
from datetime import datetime
import logging
import os
import re


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

ENV = bool(os.environ.get("ENV", False))
if ENV:
    API_ID_KEY = int(os.environ.get("API_ID_KEY"))
    API_HASH_KEY = os.environ.get("API_HASH_KEY")
    STRING_SESSION = os.environ.get("STRING_SESSION")
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    RAW_SIBYL = os.environ.get("SIBYL", "")
    RAW_ENFORCERS = os.environ.get("ENFORCERS", "")
    CHARLIE = list(int(x) for x in os.environ.get("CHARLIE", "").split())
    ADMIRALS = list(int(x) for x in os.environ.get("ADMIRALS", "").split())
    CONQUERORS = list(int(x) for x in os.environ.get("CONQUERORS", "").split())
    MONGO_DB_URL = os.environ.get("MONGO_DB_URL")
    Sibyl_logs = int(os.environ.get("Sibyl_logs"))
    Sibyl_approved_logs = int(os.environ.get("Sibyl_Approved_Logs"))
    GBAN_MSG_LOGS = int(os.environ.get("GBAN_MSG_LOGS"))
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
else:
    import Sibyl_System.config as Config

    API_ID_KEY = Config.API_ID
    API_HASH_KEY = Config.API_HASH
    STRING_SESSION = Config.STRING_SESSION
    MONGO_DB_URL = Config.MONGO_DB_URL
    with open(os.path.join(os.getcwd(), "Sibyl_System\\elevated_users.json"), "r") as f:
        data = json.load(f)
    CHARLIE = data["CHARLIE"]
    CONQUEROR = data["CONQUEROR"]
    ADMIRALS = data["ADMIRALS"]
    Sibyl_logs = Config.Sibyl_logs
    Sibyl_approved_logs = Config.Sibyl_approved_logs
    GBAN_MSG_LOGS = Config.GBAN_MSG_LOGS
    BOT_TOKEN = Config.BOT_TOKEN

ADMIRALS.extend(CHARLIE)
CONQUERORS.extend(ADMIRALS)

session = aiohttp.ClientSession()

MONGO_CLIENT = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)

from .client_class import SibylClient

System = SibylClient(StringSession(STRING_SESSION), API_ID_KEY, API_HASH_KEY)

collection = MONGO_CLIENT["Sibyl"]["Main"]


async def make_collections() -> str:
    if (
        await collection.count_documents({"_id": 1}, limit=1) == 0
    ):  # Blacklisted words list
        dictw = {"_id": 1}
        dictw["blacklisted"] = []
        await collection.insert_one(dictw)

    if (
        await collection.count_documents({"_id": 2}, limit=1) == 0
    ):  # Blacklisted words in name list
        dictw = {"_id": 2, "Type": "Wlc Blacklist"}
        dictw["blacklisted_wlc"] = []
        await collection.insert_one(dictw)
    if await collection.count_documents({"_id": 3}, limit=1) == 0:  # Gbanned users list
        dictw = {"_id": 3, "Type": "Gban:List"}
        dictw["victim"] = []
        dictw["gbanners"] = []
        dictw["reason"] = []
        dictw["proof_id"] = []
        await collection.insert_one(dictw)
    if await collection.count_documents({"_id": 4}, limit=1) == 0:  # Rank tree list
        sample_dict = {"_id": 4, "data": {}, "standalone": {}}
        sample_dict["data"] = {}
        for x in CHARLIE:
            sample_dict["data"][str(x)] = {}
            sample_dict["standalone"][str(x)] = {
                "added_by": 777000,
                "timestamp": datetime.timestamp(datetime.now()),
            }
        await collection.insert_one(sample_dict)
    return ""


def system_cmd(
    pattern=None,
    allow_charlie=True,
    allow_conquerors=False,
    allow_admirals=False,
    allow_slash=True,
    force_reply=False,
    **args
):
    if pattern and allow_slash:
        args["pattern"] = re.compile(r"[\?\.!/]" + pattern)
    else:
        args["pattern"] = re.compile(r"[\?\.!]" + pattern)
    
    elif allow_admirals and allow_charlie:
        args["from_users"] = ADMIRALS
    else:
        args["from_users"] = CHARLIE
    if force_reply:
        args["func"] = lambda e: e.is_reply
    return events.NewMessage(**args)
