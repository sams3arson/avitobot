async def process_request(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE

    wait_msg = await message.reply("Идет обработка вашего запроса...")

    raw_query = message.text.strip().split("\n")
    text_query = raw_query[0]
    min_price = int(raw_query[1].strip()) if len(raw_query) > 1 else 0
    max_price = int(raw_query[2].strip()) if len(raw_query) > 2 else 0
    page_limit = int(raw_query[3].strip()) if len(raw_query) > 3 else 0
    sorting = int(raw_query[4].strip()) if len(raw_query) > 4 else 0

    if sorting not in range(0, 4):
        sorting = 0

    city = user_city.get(user_id)
    if not city:
        city = settings.DEFAULT_CITY

    request = avito_api.Request(query=text_query, city=city, min_price=min_price,
                                max_price= max_price,  page_limit=page_limit,
                                sorting=sorting)

    result = await avito.process_request(request)

    db_cursor.execute("INSERT INTO request (query, is_tracked, url, user_id, "
                      "page_limit, sorting, min_price, max_price) VALUES "
                      "(?, ?, ?, ?, ?, ?, ?, ?)",
                      (request.query, 0, result.url, user_id, request.page_limit,
                       request.sorting, request.min_price, request.max_price))
    db_cursor.execute("SELECT last_insert_rowid()")
    insert_rowid = db_cursor.fetchall()[0][0]
    db_conn.commit()

    markup = InlineKeyboardMarkup([[InlineKeyboardButton("Отслеживать этот запрос",
                                 callback_data=f"TRACK_REQUEST={insert_rowid}")]])
    await wait_msg.delete()
    await message.reply(format_request_result(result), reply_markup=markup,
                        disable_web_page_preview=True)

