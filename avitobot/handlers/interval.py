async def interval(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_INTERVAL
    await message.reply("Введите интервал (в минутах) проверки объявлений по "
                        "вашим запросам:")

