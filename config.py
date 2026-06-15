import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

DB_PATH = "bot_data.db"

ALLOWED_MEDIA_TIMES = [10, 20, 30]
DEFAULT_MEDIA_DELETE_TIME = 30
