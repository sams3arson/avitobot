from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
import asyncio

from avitobot.states import State
from avitobot.services import jobs
from avitobot import (
    avito,
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

    app = Client("avitobot", ***REMOVED***API_ID, ***REMOVED***API_HASH, ***REMOVED***BOT_TOKEN)

    jobs.start_pings(app)
    jobs.start_track_requests(app)

    app.add_handler(MessageHandler(handlers.ignore, ~filters.private |
                                   ~filters.user(allowed_users)))
    app.add_handler(MessageHandler(handlers.start_and_help, filters.command(["help", "start"])))
    app.add_handler(MessageHandler(handlers.city, filters.command(["city"])))
    app.add_handler(MessageHandler(handlers.interval, filters.command(["interval"])))
    app.add_handler(MessageHandler(handlers.status, filters.command(["status"])))
    app.add_handler(MessageHandler(handlers.ping, filters.command(["ping"])))
    app.add_handler(MessageHandler(handlers.request, filters.command(["request"])))
    app.add_handler(MessageHandler(handlers.stop, filters.command(["stop"])))

    app.add_handler(MessageHandler(handlers.process_request, filters.create(
        wrappers.filter_state_wrapper(State.INPUT_REQUEST, user_states))))
    app.add_handler(MessageHandler(handlers.process_city, filters.create(
        wrappers.filter_state_wrapper(State.INPUT_CITY, user_states))))
    app.add_handler(MessageHandler(handlers.process_interval, filters.create(
        wrappers.filter_state_wrapper(State.INPUT_INTERVAL, user_states))))

    app.add_handler(CallbackQueryHandler(handlers.enable_track_request, filters.create(
        wrappers.filter_callback_wrapper(settings.TRACK_REQUEST_PATTERN))))
    app.add_handler(CallbackQueryHandler(handlers.process_stop, filters.create(
        wrappers.filter_callback_wrapper(settings.STOP_TRACK_REQUEST_PATTERN))))

    app.add_handler(MessageHandler(handlers.any_message))

    await app.start()

    scheduler.start()

    await idle()

    await app.stop()
    await avito.close_browser()


if __name__ == "__main__":
    asyncio.run(main())
