from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup,\
        CallbackQuery
from pathlib import Path
from tools import creds
from states import State
from custom_types import UserId, CachedMarkup
from transliterate import translit
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
import asyncio
import database
import settings
import texts
import wrappers
import avito_api
import re

credentials = creds.get(Path(settings.CREDS_FILE))
api_id, api_hash, bot_token, owner_id = credentials.api_id, credentials.api_hash,\
        credentials.bot_token, credentials.owner_id

db_conn = database.initialize()
db_cursor = db_conn.cursor()

allowed_users: list[UserId] = [owner_id] + database.get_allowed_users(db_conn)
user_city: dict[UserId, str] = database.get_user_cities(db_conn)
user_interval: dict[UserId, int] = database.get_user_intervals(db_conn)
user_ping: set[UserId] = database.get_user_pings(db_conn)
user_track_req: set[UserId] = database.get_user_track_reqs(db_conn)

ping_job: dict[UserId, Job] = dict()
track_req_job: dict[UserId, Job] = dict()

user_states: dict[UserId, State] = dict()

user_cached_markup: dict[UserId, CachedMarkup] = dict()

scheduler = AsyncIOScheduler()
avito = avito_api.Avito()
app = Client("avitobot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


def format_request_result(req_result: avito_api.RequestResult) -> str:
    return texts.REQUEST_RESULT.format(min_price=req_result.min_price,
               max_price=req_result.max_price, avg_price=req_result.avg_price,
                           ads_count=req_result.ads_count, url=req_result.url)


def start_ping_job(client: Client, user_id: UserId) -> Job:
    return scheduler.add_job(send_ping, "interval", hours=4, args=(client, user_id))


def start_pings(client: Client) -> None:
    for user_id in user_ping:
        ping_job[user_id] = start_ping_job(client, user_id)


def start_track_req_job(client: Client, user_id: UserId):
    minutes = user_interval.get(user_id)
    if not minutes:
        minutes = settings.DEFAULT_INTERVAL
    return scheduler.add_job(track_request, "interval", minutes=minutes, args=(
                                                            client, user_id))

def start_track_requests(client: Client):
    for user_id in user_track_req:
        track_req_job[user_id] = start_track_req_job(client, user_id)


async def track_request(client: Client, user_id: int) -> None:
    print("Starting track request...")
    db_cursor.execute("SELECT id, query, min_price, max_price, page_limit, "
                      "sorting FROM request WHERE user_id = ? AND is_tracked = 1",
                      (user_id,))

    city = user_city.get(user_id)
    if not city:
        city = settings.DEFAULT_CITY


    for request_raw in db_cursor.fetchall():
        await asyncio.sleep(10) # don't wanna get banned by avito
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
    print("finished track request.")


async def send_ping(client: Client, user_id: UserId) -> None:
    await client.send_message(user_id, "Бот жив.")


@app.on_message(~filters.private | ~filters.user(allowed_users))
async def ignore(client: Client, message: Message) -> None:
    """For non-private messages or messages from users that are not allowed"""
    return


@app.on_message(filters.command(["help", "start"]))
async def start(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE
    await message.reply(texts.HELP_TEXT)


@app.on_message(filters.command(["city"]))
async def city(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_CITY
    await message.reply("Введите название населенного пункта, в котором нужно "
                        "искать объявления:")


@app.on_message(filters.command(["interval"]))
async def interval(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_INTERVAL
    await message.reply("Введите интервал (в минутах) проверки объявлений по "
                        "вашим запросам:")


@app.on_message(filters.command(["status"]))
async def status(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    db_cursor.execute("SELECT human_name FROM city WHERE user_id = ?",
                             (user_id,))
    city_raw = db_cursor.fetchall()
    if city_raw:
        city = city_raw[0][0]
    else:
        city = settings.DEFAULT_HUMAN_CITY

    db_cursor.execute("SELECT query FROM request WHERE user_id = ? AND is_tracked = 1",
                                     (user_id,))
    request_names = [row[0] for row in db_cursor.fetchall()]
    request_amount = len(request_names)

    db_cursor.execute("SELECT interval_len FROM interval WHERE user_id = ?",
                      (user_id,))
    interval_raw = db_cursor.fetchall()
    if interval_raw:
        interval = str(interval_raw[0][0])
    else:
        interval = str(settings.DEFAULT_INTERVAL)

    db_cursor.execute("SELECT id FROM ping WHERE user_id = ?", (user_id,))
    ping_raw = db_cursor.fetchall()
    if ping_raw:
        ping = "включены"
    else:
        ping = "выключены"

    answer = texts.STATUS.format(city=city, interval=interval, ping=ping,
                                 request_amount=request_amount)
    if request_names:
        answer += "Активные запросы:\n"
    for req_name in request_names:
        answer += f"- {req_name}\n"

    await message.reply(answer)


@app.on_message(filters.command(["ping"]))
async def ping(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE
    
    if user_id in user_ping:
        user_ping.remove(user_id)
        db_cursor.execute("DELETE FROM ping WHERE user_id = ?", (user_id,))
        db_conn.commit()
        ping_job[user_id].remove()
        await message.reply("Сообщения о состоянии бота отключены.")
        return

    user_ping.add(user_id)
    db_cursor.execute("INSERT INTO ping (user_id) VALUES (?)", (user_id,))
    db_conn.commit()
    ping_job[user_id] = start_ping_job(client, user_id)
    await message.reply("Сообщения о состоянии бота будут отправляться вам каждые "
                        "4 часа.")


@app.on_message(filters.command(["request"]))
async def request(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.INPUT_REQUEST
    await message.reply("Введите детали запроса: в 1 строке - сам запрос, во 2 - "
                        "минимальную цену (необязательно), и в 3 - максимальную "
                        "(необязательно), в 4 - лимит кол-ва страниц, "
                        " в 5 - сортировку (необязательно).\n\n"
                        "Сортировка:\n1 - дешевле, 2 - дороже, 3 - по дате.")


@app.on_message(filters.command(["stop"]))
async def stop(client: Client, message: Message) -> None:
    user_id = message.from_user.id

    db_cursor.execute("SELECT query, id FROM request WHERE user_id = ? "
                      "AND is_tracked = 1", (user_id,))
    requests_raw = db_cursor.fetchall()

    if not requests_raw:
        await message.reply("У вас нет отслеживаемых запросов.")
        return

    buttons = list()
    row = list()
    for req_row in requests_raw:
        if len(row) == 2:
            buttons.append(row)
            row = list()
        row.append(InlineKeyboardButton(req_row[0], callback_data=
                                        f"STOP_TRACK_REQUEST={req_row[1]}"))
    buttons.append(row)

    markup = buttons[0:3]
    if len(buttons) > 3:
        markup.append([InlineKeyboardButton("➡️ На следующую страницу",
                                            callback_data=f"SWITCH_PAGE=3_6")])
    await message.reply("Выберите запрос, который больше не нужно отслеживать:",
                        reply_markup=InlineKeyboardMarkup(markup))
    user_cached_markup[user_id] = CachedMarkup(buttons, message.id)


@app.on_message(filters.create(wrappers.filter_state_wrapper(State.INPUT_REQUEST,
                                                             user_states)))
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


@app.on_message(filters.create(wrappers.filter_state_wrapper(State.INPUT_CITY,
                                                             user_states)))
async def process_city(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE

    city_human = message.text.title()
    city_text = translit(city_human.lower(), "ru", reversed=True).replace("j",
                                                          "y").replace(" ", "_")
    msg = await message.reply("Обрабатываем запрос...")
    if not avito.check_city(city_text):
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


@app.on_message(filters.create(wrappers.filter_state_wrapper(State.INPUT_INTERVAL,
                                                             user_states)))
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


@app.on_callback_query(filters.create(wrappers.filter_callback_wrapper(
                                            settings.TRACK_REQUEST_PATTERN)))
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


@app.on_callback_query(filters.create(wrappers.filter_callback_wrapper(
                                        settings.STOP_TRACK_REQUEST_PATTERN)))
async def process_stop(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    callback_data = callback_query.data

    match = re.search(settings.STOP_TRACK_REQUEST_PATTERN, callback_data)
    request_id = match.group(1)

    db_cursor.execute("UPDATE request SET is_tracked = 0 WHERE id = ?",
                      (request_id,))
    db_conn.commit()
    await callback_query.answer("Этот запрос больше не отслеживается.")


@app.on_callback_query(filters.create(wrappers.filter_callback_wrapper(
                                                settings.SWITCH_PAGE_PATTERN)))
async def swtich_page(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    callback_data = callback_query.data

    match = re.search(settings.SWITCH_PAGE_PATTERN, callback_data)
    start_page, end_page = int(match.group(1)), int(match.group(2))

    cached_markup = user_cached_markup.get(user_id)
    if not cached_markup:
        await client.send_message(user_id, "Этот сообщение слишком старое, чтобы "
                  "интерактировать с ним. Запросите новое и работайте с ним.")
        return

    buttons, msg_id = cached_markup

    markup = buttons[start_page:end_page]
    arrows = []
    if start_page > 0:
        arrows.append(InlineKeyboardButton("⬅️ На предыдущую страницу",
                    callback_data=f"SWITCH_PAGE={start_page - 3}_{end_page - 3}"))
    if len(buttons) > end_page:
        arrows.append(InlineKeyboardButton("➡️ На следующую страницу",
                        callback_data=f"SWITCH_PAGE={start_page + 3}_{end_page + 3}"))
    markup.append(arrows)
    await callback_query.message.edit_reply_markup(
            InlineKeyboardMarkup(markup))


@app.on_message()
async def any_message(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    user_states[user_id] = State.NO_STATE
    await message.reply(texts.PROVIDE_HELP)
    
start_pings(app)
start_track_requests(app)
scheduler.start()

app.run()

