async def process_interval(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE

    interval = message.text
    if not interval.isdigit():
        await message.reply("Интервал должен быть целым числом в минутах.")
        return
    interval = int(interval)
    if interval < 5:
        await message.reply("Нельзя установить интервал меньше 5 минут (риск "
                            "блокировки)")
        return

    user_interval[user_id] = interval
    db_cursor.execute("DELETE FROM interval WHERE user_id = ?", (user_id,))
    db_cursor.execute("INSERT INTO interval (interval_len, user_id) VALUES (?, ?)",
                      (interval, user_id))
    db_conn.commit()

    if user_id in track_req_job:
        track_req_job[user_id].remove()
        track_req_job[user_id] = start_track_req_job(client, user_id)

    await message.reply(f"Теперь интервал проверки объявлений составляет {interval} "
                        "минут.")

