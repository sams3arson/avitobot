from pyrogram import Client
from pyrogram.types import Message
from transliterate import translit

from avitobot.services import jobs
from avitobot.states import State
from avitobot import (
    db,
    user_states,
    user_city,
    avito
)


async def process_city(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE

    city_human = message.text.title()
    city_text = translit(city_human.lower(), "ru", reversed=True).replace("j",
                                                          "y").replace(" ", "_")
    msg = await message.reply("Обрабатываем запрос...")
    if not await avito.check_city(city_text):
        await msg.delete()
        await message.reply("Не удалось настроить поиск по указанному "
                "населенному пункту. Проверьте правильность слова и попробуйте "
                "еще раз")
        return

    await msg.delete()
    user_city[user_id] = city_text
    await db.execute("DELETE FROM city WHERE user_id = ?", (user_id,))
    await db.execute("INSERT INTO city (name, human_name, user_id) VALUES (?, ?, ?)",
                    (city_text, city_human, user_id))
    await message.reply("Поиск успешно настроен по указанному населенному пункту.")

