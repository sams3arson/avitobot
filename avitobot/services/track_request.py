async def track_request(client: Client, user_id: int) -> None:
    db_cursor.execute("SELECT id, query, min_price, max_price, page_limit, "
                      "sorting FROM request WHERE user_id = ? AND is_tracked = 1",
                      (user_id,))

    city = user_city.get(user_id)
    if not city:
        city = settings.DEFAULT_CITY


    for request_raw in db_cursor.fetchall():
        await asyncio.sleep(random.randint(7, 13)) # don't wanna get banned by avito
        request = avito_api.Request(query=request_raw[1], city=city,
                                    min_price=request_raw[2], max_price=
                                    request_raw[3], page_limit=request_raw[4],
                                    sorting=request_raw[5])
        request_rowid = request_raw[0]
        result = await avito.process_request(request)

        db_cursor.execute("SELECT name, description, price, avito_id FROM "
                          "product WHERE request_id = ?", (request_rowid,))
        products = {product_raw[3]: {"name": product_raw[0], "description":
                                     product_raw[1], "price": product_raw[2]}
                    for product_raw in db_cursor.fetchall()}
        
        for product in result.ads_list:
            if product.avito_id not in products:
                await client.send_message(user_id, texts.NEW_AD.format(
                    query=request.query, name=product.name, description=
                    product.description[:500], price=product.price, url=
                    product.url), disable_web_page_preview=True)
                
                db_cursor.execute("INSERT INTO product (name, description, price, "
                "avito_id, url) VALUES (?, ?, ?, ?, ?)", (product.name, 
                product.description, product.price, product.avito_id, product.url))
            
            elif product.price != products[product.avito_id]["price"]:
                await client.send_message(user_id, texts.AD_PRICE_CHANGE.format(
                    query=request.query, name=product.name, old_price=
                    products[product.avito_id]["price"], new_price=product.price,
                    description=product.description, url=product.url),
                                          disable_web_page_preview=True)

                db_cursor.execute("UPDATE product SET price = ? WHERE avito_id "
                                  "= ?", (product.price, product.avito_id))
        db_conn.commit()

