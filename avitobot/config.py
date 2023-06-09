from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CREDS_FILE = BASE_DIR / "config.ini"
DB_FILE = BASE_DIR / "avitobot.db"
DB_CONFIG = BASE_DIR / "avitobot.sql"
AVITO_BASE = "https://www.avito.ru"
AVITO_URL = "https://www.avito.ru/{city}?q={query}&s={sorting}"
AVITO_CITY = "https://www.avito.ru/{city}"
DEFAULT_CITY = "rossiya"
DEFAULT_HUMAN_CITY = "Россия"
DEFAULT_INTERVAL = 30
TRACK_REQUEST_PATTERN = r"^TRACK_REQUEST=(\d+)"
STOP_TRACK_REQUEST_PATTERN = r"^STOP_TRACK_REQUEST=(\d+)"
SWITCH_PAGE_PATTERN = r"SWITCH_PAGE=(\d+)_(\d+)"
MAX_PAGE_LIMIT = 5
