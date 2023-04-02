from pyrogram import Client
from pyrogram.types import Message

from avitobot.states import State
from avitobot import user_states


async def request(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_REQUEST
    await message.reply("Введите детали запроса: в 1 строке - сам запрос, во 2 - "
                        "минимальную цену (необязательно), и в 3 - максимальную "
                        "(необязательно), в 4 - лимит кол-ва страниц, "
                        " в 5 - сортировку (необязательно).\n\n"
                        "Сортировка:\n1 - дешевле, 2 - дороже, 3 - по дате.")
