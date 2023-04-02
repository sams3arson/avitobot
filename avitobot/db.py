import aiosqlite
from avitobot import settings

async def get_db() -> aiosqlite.Connection:
    if not getattr(get_db, "db", None):
        db = await aiosqlite.connect(settings.DB_FILE)
        get_db.db = db

    return get_db.db


async def fetch_one(sql: str) -> dict | None:
    cursor = await _get_cursor()
    await cursor.execute(sql)
    row = await cursor.fetchone()
    if not row:
        return None

    result = _get_result_with_column_names(cursor, row)
    await cursor.close()
    return result


async def fetch_all(sql: str) -> list[dict]:
    cursor = await _get_cursor()
    await cursor.execute(sql)
    rows = await cursor.fetchall()
    results = []

    for row in rows:
        results.append(_get_result_with_column_names(cursor, row))
    await cursor.close()
    return results


async def execute(sql: str, autocommit: bool = True) -> None:
    db = await get_db()
    await db.execute(sql)
    if autocommit:
        await db.commit()


async def _get_cursor() -> aiosqlite.Cursor:
    db = await get_db()
    return await db.cursor()


def _get_result_with_column_names(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> dict:
    column_names = [d[0] for d in cursor.description]
    resulting_row = {}
    for index, column_name in enumerate(column_names):
        resulting_row[column_name] = row[index]
    return resulting_row

