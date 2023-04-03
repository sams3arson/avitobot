from pyrogram import Client
import asyncio
import random

from avitobot import (
    db,
    avito_api,
    avito,
    config,
    texts,
    user_city
)


async def track_request(client: Client, user_id: int) -> None:
    requests = await db.fetch_all("SELECT id, query, min_price, max_price, page_limit, "
                                  "sorting FROM request WHERE user_id = ? AND is_tracked = 1",
                                  (user_id,))

    city = user_city.get(user_id)
    if not city:
        city = config.DEFAULT_CITY

    for request_ in requests:
        await asyncio.sleep(random.randint(7, 13))  # don't wanna get banned by avito
        request = avito_api.Request(query=request_["query"], city=city,
                                    min_price=request_["min_price"],
                                    max_price=request_["max_price"],
                                    page_limit=request_["page_limit"],
                                    sorting=request_["sorting"])
        request_rowid = request_["id"]
        result = await avito.process_request(request)

        products_ = await db.fetch_all("SELECT name, description, price, avito_id "
                                       "FROM product WHERE request_id = ?", (request_rowid,))
        products = {product["avito_id"]: {"name": product["name"], "description": product["description"],
                                          "price": product["description"]}
                    for product in products_}

        for product in result.ads_list:
            if product.avito_id not in products:
                await client.send_message(user_id, texts.NEW_AD.format(
                    query=request.query,
                    name=product.name,
                    description=product.description[:500],
                    price=product.price,
                    url=product.url),
                                          disable_web_page_preview=True)

                await db.execute("INSERT INTO product (name, description, price, "
                                 "avito_id, url) VALUES (?, ?, ?, ?, ?)", (product.name,
                                                                           product.description, product.price,
                                                                           product.avito_id, product.url))

            elif product.price != products[product.avito_id]["price"]:
                await client.send_message(user_id, texts.AD_PRICE_CHANGE.format(
                    query=request.query,
                    name=product.name,
                    old_price=products[product.avito_id]["price"],
                    new_price=product.price,
                    description=product.description,
                    url=product.url),
                                          disable_web_page_preview=True)

                await db.execute("UPDATE product SET price = ? WHERE avito_id "
                                 "= ?", (product.price, product.avito_id))
