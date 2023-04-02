from pyrogram import Client
from pyrogram.types import Message
from avitobot import texts
from avitobot.states import State

async def ping(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE
    
    if user_id in user_ping:
        user_ping.remove(user_id)
        db_cursor.execute("DELETE FROM ping WHERE user_id = ?", (user_id,))
        db_conn.commit()
        ping_job[user_id].remove()
        await message.reply("Сообщения о состоянии бота отключены.")
        return

    user_ping.add(user_id)
    db_cursor.execute("INSERT INTO ping (user_id) VALUES (?)", (user_id,))
    db_conn.commit()
    ping_job[user_id] = start_ping_job(client, user_id)
    await message.reply("Сообщения о состоянии бота будут отправляться вам каждые "
                        "4 часа.")

