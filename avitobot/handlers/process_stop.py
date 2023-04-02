async def process_stop(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    callback_data = callback_query.data

    match = re.search(settings.STOP_TRACK_REQUEST_PATTERN, callback_data)
    request_id = match.group(1)

    db_cursor.execute("UPDATE request SET is_tracked = 0 WHERE id = ?",
                      (request_id,))
    db_conn.commit()
    await callback_query.answer("Этот запрос больше не отслеживается.")

