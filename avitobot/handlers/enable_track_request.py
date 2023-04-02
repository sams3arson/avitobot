async def enable_track_request(client: Client, callback_query: CallbackQuery) \
        -> None:
    user_id = callback_query.from_user.id
    callback_data = callback_query.data
    wait_msg = await client.send_message(user_id, "Обрабатываем запрос...")

    match = re.search(settings.TRACK_REQUEST_PATTERN, callback_data)
    request_rowid = match.group(1)
    db_cursor.execute("UPDATE request SET is_tracked = 1 WHERE id = ?",
                      (request_rowid,))
    db_conn.commit()

    city = user_city.get(user_id)
    if not city:
        city = settings.DEFAULT_CITY
    db_cursor.execute("SELECT query, page_limit, sorting, min_price, max_price "
                      "FROM request WHERE id = ?", (request_rowid,))
    query, page_limit, sorting, min_price, max_price = db_cursor.fetchall()[0]
    request = avito_api.Request(query=query, city=city, min_price=min_price,
                    max_price=max_price, page_limit=page_limit, sorting=sorting)

    result = await avito.process_request(request)
    db_cursor.execute("INSERT INTO request_result (request_id, avg_price, "
                      "min_price, max_price) VALUES (?, ?, ?, ?)", (request_rowid,
                            result.avg_price, result.min_price, result.max_price))
    for product in result.ads_list:
        db_cursor.execute("INSERT INTO product (name, description, price, "
                          "avito_id, url, request_id) VALUES (?, ?, ?, ?, ?, ?)",
                          (product.name, product.description, product.price, 
                           product.avito_id, product.url, request_rowid))
    db_conn.commit()

    if user_id not in track_req_job:
        track_req_job[user_id] = start_track_req_job(client, user_id)

    await wait_msg.delete()
    await client.send_message(user_id, "Теперь объявления по этому запросу "
                              "будут отслеживаться.")

