from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
import asyncio

from avitobot.states import State
from avitobot.services import jobs
from avitobot import (
    avito,
    db,
    settings,
    wrappers,
    handlers,
    scheduler,
    API_ID,
    API_HASH,
    BOT_TOKEN,
    allowed_users,
    user_states
)


async def main():
    await avito.setup_browser()

    app = Client("avitobot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

    jobs.start_pings(app)
    jobs.start_track_requests(app)

    MESSAGE_HANDLERS = {
        handlers.ignore: (~filters.private | ~filters.user(allowed_users)),
        handlers.start_and_help: filters.command(["help", "start"]),
        handlers.city: filters.command(["city"]),
        handlers.interval: filters.command(["interval"]),
        handlers.status: filters.command(["status"]),
        handlers.ping: filters.command(["ping"]),
        handlers.request: filters.command(["request"]),
        handlers.stop: filters.command(["stop"]),
        handlers.process_request: filters.create(
            wrappers.filter_state_wrapper(State.INPUT_REQUEST, user_states)),
        handlers.process_city: filters.create(
            wrappers.filter_state_wrapper(State.INPUT_CITY, user_states)),
        handlers.process_interval: filters.create(
            wrappers.filter_state_wrapper(State.INPUT_INTERVAL, user_states)),
    }

    for handler, filter_ in MESSAGE_HANDLERS.items():
        app.add_handler(MessageHandler(handler, filter_))

    CALLBACK_HANDLERS = {
        handlers.enable_track_request: filters.create(
            wrappers.filter_callback_wrapper(settings.TRACK_REQUEST_PATTERN)),
        handlers.process_stop: filters.create(
            wrappers.filter_callback_wrapper(settings.STOP_TRACK_REQUEST_PATTERN))
    }

    for handler, filter_ in CALLBACK_HANDLERS.items():
        app.add_handler(CallbackQueryHandler(handler, filter_))

    app.add_handler(MessageHandler(handlers.any_message))

    await app.start()
    scheduler.start()
    await idle()

    await db.close_db()
    await avito.close_browser()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
