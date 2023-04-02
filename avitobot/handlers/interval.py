from pyrogram import Client
from pyrogram.types import Message
from avitobot.states import State
from avitobot import user_states


async def interval(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_INTERVAL
    await message.reply("Введите интервал (в минутах) проверки объявлений по "
                        "вашим запросам:")

