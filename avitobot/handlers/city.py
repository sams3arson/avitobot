from pyrogram import Client
from pyrogram.types import Message
from avitobot import user_states
from avitobot.states import State

async def city(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_CITY
    await message.reply("Введите название населенного пункта, в котором нужно "
                        "искать объявления:")

