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
    db_cursor.execute("DELETE FROM city WHERE user_id = ?", (user_id,))
    db_cursor.execute("INSERT INTO city (name, human_name, user_id) VALUES (?, ?, ?)",
                    (city_text, city_human, user_id))
    db_conn.commit()
    await message.reply("Поиск успешно настроен по указанному населенному пункту.")

