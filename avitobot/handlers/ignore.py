from pyrogram import Client
from pyrogram.types import Message


async def ignore(client: Client, message: Message) -> None:
    """For non-private messages or messages from users that are not allowed"""
    return
