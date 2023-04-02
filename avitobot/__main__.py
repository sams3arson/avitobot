from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup,\
        CallbackQuery
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pathlib import Path
from transliterate import translit
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from avitobot import database, texts, settings, wrappers, avito_api
from avitobot.tools import creds
from avitobot.states import State
from avitobot.custom_types import UserId, CachedMarkup
import asyncio
import random
import re

credentials = creds.get(settings.CREDS_FILE)
api_id, api_hash, bot_token, owner_id = credentials.api_id, credentials.api_hash,\
        credentials.bot_token, credentials.owner_id

db_conn = database.initialize()
db_cursor = db_conn.cursor()

allowed_users: list[UserId] = [owner_id] + database.get_allowed_users(db_conn)
user_city: dict[UserId, str] = database.get_user_cities(db_conn)
user_interval: dict[UserId, int] = database.get_user_intervals(db_conn)
user_ping: set[UserId] = database.get_user_pings(db_conn)
user_track_req: set[UserId] = database.get_user_track_reqs(db_conn)

ping_job: dict[UserId, Job] = dict()
track_req_job: dict[UserId, Job] = dict()

user_states: dict[UserId, State] = dict()

user_cached_markup: dict[UserId, CachedMarkup] = dict()

scheduler = AsyncIOScheduler()
avito = avito_api.Avito()

def format_request_result(req_result: avito_api.RequestResult) -> str:
    return texts.REQUEST_RESULT.format(min_price=req_result.min_price,
               max_price=req_result.max_price, avg_price=req_result.avg_price,
                           ads_count=req_result.ads_count, url=req_result.url)


def start_ping_job(client: Client, user_id: UserId) -> Job:
    return scheduler.add_job(send_ping, "interval", hours=4, args=(client, user_id))


def start_pings(client: Client) -> None:
    for user_id in user_ping:
        ping_job[user_id] = start_ping_job(client, user_id)


def start_track_req_job(client: Client, user_id: UserId):
    minutes = user_interval.get(user_id)
    if not minutes:
        minutes = settings.DEFAULT_INTERVAL
    return scheduler.add_job(track_request, "interval", minutes=minutes, args=(
                                                            client, user_id))


def start_track_requests(client: Client):
    for user_id in user_track_req:
        track_req_job[user_id] = start_track_req_job(client, user_id)


async def send_ping(client: Client, user_id: UserId) -> None:
    await client.send_message(user_id, "Бот жив.")


async def main():
    await avito.setup_browser()

    app = Client("avitobot", ***REMOVED***api_id, ***REMOVED***api_hash, ***REMOVED***bot_token)

    start_pings(app)
    start_track_requests(app)

    app.add_handler(MessageHandler(ignore, ~filters.private | 
                                   ~filters.user(allowed_users)))
    app.add_handler(MessageHandler(start, filters.command(["help", "start"])))
    app.add_handler(MessageHandler(city, filters.command(["city"])))
    app.add_handler(MessageHandler(interval, filters.command(["interval"])))
    app.add_handler(MessageHandler(status, filters.command(["status"])))
    app.add_handler(MessageHandler(ping, filters.command(["ping"])))
    app.add_handler(MessageHandler(request, filters.command(["request"])))
    app.add_handler(MessageHandler(stop, filters.command(["stop"])))


    app.add_handler(MessageHandler(process_request, filters.create(
        wrappers.filter_state_wrapper(State.INPUT_REQUEST, user_states))))
    app.add_handler(MessageHandler(process_city, filters.create(
        wrappers.filter_state_wrapper(State.INPUT_CITY, user_states))))
    app.add_handler(MessageHandler(process_interval, filters.create(
        wrappers.filter_state_wrapper(State.INPUT_INTERVAL, user_states))))

    app.add_handler(CallbackQueryHandler(enable_track_request, filters.create(
        wrappers.filter_callback_wrapper(settings.TRACK_REQUEST_PATTERN))))
    app.add_handler(CallbackQueryHandler(process_stop, filters.create(
        wrappers.filter_callback_wrapper(settings.STOP_TRACK_REQUEST_PATTERN))))

    app.add_handler(MessageHandler(any_message))


    await app.start()

    scheduler.start()

    await idle()

    await app.stop()
    await avito.close_browser()


if __name__ == "__main__":
    asyncio.run(main())

