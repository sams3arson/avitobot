async def city(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_CITY
    await message.reply("Введите название населенного пункта, в котором нужно "
                        "искать объявления:")

