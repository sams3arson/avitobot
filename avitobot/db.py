import aiosqlite
from avitobot import config
from typing import Iterable, Any

async def get_db() -> aiosqlite.Connection:
    if not getattr(get_db, "db", None):
        db = await aiosqlite.connect(config.DB_FILE)
        get_db.db = db

    return get_db.db


async def close_db() -> None:
    await (await get_db()).close()


async def fetch_one(sql: str, params: Iterable[Any] | None = None) -> dict | None:
    cursor = await _get_cursor()
    await cursor.execute(sql, params)
    row = await cursor.fetchone()
    if not row:
        return None

    result = _get_result_with_column_names(cursor, row)
    await cursor.close()
    return result


async def fetch_all(sql: str, params: Iterable[Any] | None = None) -> list[dict]:
    cursor = await _get_cursor()
    await cursor.execute(sql, params)
    rows = await cursor.fetchall()
    results = []

    for row in rows:
        results.append(_get_result_with_column_names(cursor, row))
    await cursor.close()
    return results


async def execute(
    sql: str, params: Iterable[Any] | None = None, *, autocommit: bool = True
) -> None:
    db = await get_db()
    await db.execute(sql, params)
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

