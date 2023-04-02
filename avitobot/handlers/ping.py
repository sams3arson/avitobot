from pyrogram import Client
from pyrogram.types import Message

from avitobot.states import State
from avitobot.services import jobs
from avitobot import (
    db,
    user_states,
    user_ping,
    ping_jobs
)

async def ping(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE
    
    if user_id in user_ping:
        user_ping.remove(user_id)
        await db.execute("DELETE FROM ping WHERE user_id = ?", (user_id,))
        ping_jobs[user_id].remove()
        await message.reply("Сообщения о состоянии бота отключены.")
        return

    user_ping.add(user_id)
    await db.execute("INSERT INTO ping (user_id) VALUES (?)", (user_id,))
    ping_jobs[user_id] = jobs.start_ping_job(client, user_id)
    await message.reply("Сообщения о состоянии бота будут отправляться вам каждые "
                        "4 часа.")
