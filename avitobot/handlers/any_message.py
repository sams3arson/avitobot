from pyrogram import Client
from pyrogram.types import Message
from avitobot import texts

async def any_message(client: Client, message: Message) -> None:
    await message.reply(texts.PROVIDE_HELP)

