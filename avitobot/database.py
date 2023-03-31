import sqlite3
from avitobot import settings
from avitobot.custom_types import UserId

def initialize() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_FILE)
    return conn


def get_allowed_users(db_connection: sqlite3.Connection) -> list[UserId]:
    cursor = db_connection.cursor()
    cursor.execute("SELECT telegram_id FROM user")
    user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids


def get_user_cities(db_connection: sqlite3.Connection) -> dict[UserId, str]:
    cursor = db_connection.cursor()
    cursor.execute("SELECT user_id, name FROM city");
    city_raw = cursor.fetchall()

    city_dict = {user_id: city_name for user_id, city_name in city_raw}
    return city_dict


def get_user_intervals(db_connection: sqlite3.Connection) -> dict[UserId, int]:
    cursor = db_connection.cursor()
    cursor.execute("SELECT user_id, interval_len FROM interval");
    interval_raw = cursor.fetchall()

    interval_dict = {user_id: interval for user_id, interval in interval_raw}
    return interval_dict


def get_user_pings(db_connection: sqlite3.Connection) -> set[UserId]:
    cursor = db_connection.cursor()
    cursor.execute("SELECT user_id FROM ping")
    pings_raw = cursor.fetchall()
    
    pings = {user_id[0] for user_id in pings_raw}
    return pings


def get_user_track_reqs(db_connection: sqlite3.Connection) -> set[UserId]:
    cursor = db_connection.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM request WHERE is_tracked = 1")
    tracks_raw = cursor.fetchall()

    tracks = {user_id[0] for user_id in tracks_raw}
    return tracks

