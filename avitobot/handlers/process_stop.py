from pyrogram import Client
from pyrogram.types import CallbackQuery
import re

from avitobot import settings
from avitobot import db

async def process_stop(client: Client, callback_query: CallbackQuery):
    callback_data = callback_query.data

    match = re.search(settings.STOP_TRACK_REQUEST_PATTERN, callback_data)
    request_id = match.group(1)

    await db.execute("UPDATE request SET is_tracked = 0 WHERE id = ?",
                      (request_id,))
    await callback_query.answer("Этот запрос больше не отслеживается.")

