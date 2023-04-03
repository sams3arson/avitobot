from pyrogram import Client
from pyrogram.types import Message

from avitobot import texts, config
from avitobot import (
    db,

)


async def status(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    city_ = await db.fetch_one("SELECT human_name FROM city WHERE user_id = ?",
                               (user_id,))
    if city_:
        city = city_["human_name"]
    else:
        city = config.DEFAULT_HUMAN_CITY

    requests = await db.fetch_all("SELECT query FROM request WHERE user_id = ? "
                                  "AND is_tracked = 1", (user_id,))
    request_names = [row["query"] for row in requests]
    request_amount = len(request_names)

    interval_ = await db.fetch_one("SELECT interval_len FROM interval WHERE "
                                   "user_id = ?", (user_id,))
    if interval_:
        interval = str(interval_["interval_len"])
    else:
        interval = str(config.DEFAULT_INTERVAL)

    ping_ = await db.fetch_one("SELECT id FROM ping WHERE user_id = ?", (user_id,))
    if ping_:
        ping = "включены"
    else:
        ping = "выключены"

    answer = texts.STATUS.format(city=city, interval=interval, ping=ping,
                                 request_amount=request_amount)
    if request_names:
        answer += "Активные запросы:\n"
    for req_name in request_names:
        answer += f"- {req_name}\n"

    await message.reply(answer)
