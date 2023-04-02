from pyrogram import Client
from pyrogram.types import Message
from avitobot import texts, settings

async def status(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    db_cursor.execute("SELECT human_name FROM city WHERE user_id = ?",
                             (user_id,))
    city_raw = db_cursor.fetchall()
    if city_raw:
        city = city_raw[0][0]
    else:
        city = settings.DEFAULT_HUMAN_CITY

    db_cursor.execute("SELECT query FROM request WHERE user_id = ? AND is_tracked = 1",
                                     (user_id,))
    request_names = [row[0] for row in db_cursor.fetchall()]
    request_amount = len(request_names)

    db_cursor.execute("SELECT interval_len FROM interval WHERE user_id = ?",
                      (user_id,))
    interval_raw = db_cursor.fetchall()
    if interval_raw:
        interval = str(interval_raw[0][0])
    else:
        interval = str(settings.DEFAULT_INTERVAL)

    db_cursor.execute("SELECT id FROM ping WHERE user_id = ?", (user_id,))
    ping_raw = db_cursor.fetchall()
    if ping_raw:
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

