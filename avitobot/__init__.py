from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
import asyncio

from avitobot.custom_types import UserId, CachedMarkup
from avitobot.tools import credentials
from avitobot.tools.states import State
from avitobot import config, avito_api, db

SQL_STRINGS = {
    "allowed_users": "SELECT telegram_id FROM user",
    "user_city": "SELECT user_id, name FROM city",
    "user_interval": "SELECT user_id, interval_len FROM interval",
    "user_ping": "SELECT user_id FROM ping",
    "user_track_request": "SELECT DISTINCT user_id FROM request WHERE is_tracked = 1",
}

credentials_ = credentials.get(config.CREDS_FILE)
API_ID, API_HASH, BOT_TOKEN, OWNER_ID = credentials_.api_id, credentials_.api_hash, \
    credentials_.bot_token, credentials_.owner_id

allowed_users: list[UserId] = [OWNER_ID] + [row["user_id"] for row in
                        asyncio.run(db.fetch_all(SQL_STRINGS["allowed_users"]))]

user_city: dict[UserId, str] = {row["user_id"]: row["name"] for row in
                            asyncio.run(db.fetch_all(SQL_STRINGS["user_city"]))}

user_interval: dict[UserId, int] = {row["user_id"]: row["interval_len"] for row
                    in asyncio.run(db.fetch_all(SQL_STRINGS["user_interval"]))}

user_ping: set[UserId] = {row["user_id"] for row in asyncio.run(db.fetch_all(
    SQL_STRINGS["user_ping"]))}

user_track_request: set[UserId] = {row["user_id"] for row in asyncio.run(db.fetch_all(
    SQL_STRINGS["user_track_request"]))}

ping_jobs: dict[UserId, Job] = dict()
track_request_jobs: dict[UserId, Job] = dict()

user_states: dict[UserId, State] = dict()

user_cached_markup: dict[UserId, CachedMarkup] = dict()

scheduler = AsyncIOScheduler()
avito = avito_api.Avito()
