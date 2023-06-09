from pyrogram import Client
from pyrogram.types import Message

from avitobot.tools.states import State
from avitobot import (
    user_states,
    texts
)


async def start_and_help(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE
    await message.reply(texts.HELP_TEXT)
