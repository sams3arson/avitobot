from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from avitobot.custom_types import CachedMarkup
from avitobot import (
    db,
    user_cached_markup,
)


async def stop(client: Client, message: Message) -> None:
    user_id = message.from_user.id

    requests = await db.fetch_all("SELECT query, id FROM request WHERE user_id = ? "
                                  "AND is_tracked = 1", (user_id,))

    if not requests:
        await message.reply("У вас нет отслеживаемых запросов.")
        return

    buttons = list()
    row = list()
    for req_row in requests:
        if len(row) == 2:
            buttons.append(row)
            row = list()
        row.append(InlineKeyboardButton(req_row["query"],
                            callback_data=f"STOP_TRACK_REQUEST={req_row['id']}"))
    buttons.append(row)

    markup = buttons[0:3]
    if len(buttons) > 3:
        markup.append([InlineKeyboardButton("➡️ На следующую страницу",
                                            callback_data=f"SWITCH_PAGE=3_6")])
    await message.reply("Выберите запрос, который больше не нужно отслеживать:",
                        reply_markup=InlineKeyboardMarkup(markup))
    user_cached_markup[user_id] = CachedMarkup(buttons, message.id)
