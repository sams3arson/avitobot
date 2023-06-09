HELP_TEXT = """Привет!
Это бот, с помощью которого можно отслеживать объявления на Авито: появления \
новых, изменения цен на старых, общая статистика по объявлениям (по \
конкретным запросам).

Команды:
/help - получить справку
/city - установить город для поиска объявлений
/status - просмотреть свои запросы и настройки
/interval - настроить интервал проверки объявлений по вашим запросам
/ping - включить/выключить автоматические сообщения о состоянии бота каждые 4 часа
/request - сделать поиск объявлений по запросу и отправить статистику
/stop - перестать отслеживать объявления
"""
PROVIDE_HELP = "Для получения справки используйте команду /help."
REQUEST_RESULT = """Кол-во объявлений: {ads_count}

Средняя цена: {avg_price}
Минимальная цена: {min_price}
Максимальная цена: {max_price}

Просмотреть объявления: {url}
"""
STATUS = """Ваш населенный пункт: {city}
Интервал проверки объявлений по запросам: {interval} минут
Сообщения о состоянии бота: {ping}
Количество активных запросов: {request_amount}\n\n"""
NEW_AD = """Появилось новое объявление по запросу "{query}":
Название: {name}
Цена: {price}
Описание: {description}
Ссылка: {url}
"""
AD_PRICE_CHANGE = """По запросу "{query}" у объявления "{name}" изменилась цена:
c {old_price} на {new_price}.
Описание: {description}
Ссылка: {url}
"""

