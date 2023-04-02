async def switch_page(client: Client, callback_query: CallbackQuery):
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

