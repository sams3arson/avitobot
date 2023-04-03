from pyrogram import Client
from pyrogram.types import Message

from avitobot.tools.states import State
from avitobot.services import jobs
from avitobot import (
    db,
    user_states,
    user_interval,
    track_request_jobs
)


async def process_interval(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE

    interval = message.text
    if not interval.isdigit():
        await message.reply("Интервал должен быть целым числом в минутах.")
        return
    interval = int(interval)
    if interval < 5:
        await message.reply("Нельзя установить интервал меньше 5 минут (риск "
                            "блокировки)")
        return

    user_interval[user_id] = interval
    await db.execute("DELETE FROM interval WHERE user_id = ?", (user_id,))
    await db.execute("INSERT INTO interval (interval_len, user_id) VALUES (?, ?)",
                     (interval, user_id))

    if user_id in track_request_jobs:
        track_request_jobs[user_id].remove()
        track_request_jobs[user_id] = jobs.start_track_request_job(client, user_id)

    await message.reply(f"Теперь интервал проверки объявлений составляет {interval} "
                        "минут.")
