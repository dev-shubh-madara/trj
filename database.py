import sqlite3
import threading
from config import DB_PATH

_local = threading.local()


def get_conn():
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS authorized_users (user_id INTEGER PRIMARY KEY)""")

    c.execute("""CREATE TABLE IF NOT EXISTS certified_users (
        user_id INTEGER, chat_id INTEGER, PRIMARY KEY (user_id, chat_id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS group_settings (
        chat_id INTEGER PRIMARY KEY,
        media_delete_time INTEGER DEFAULT 30,
        group_title TEXT,
        group_photo_id TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS warns (
        user_id INTEGER, chat_id INTEGER, count INTEGER DEFAULT 0,
        reasons TEXT DEFAULT '',
        PRIMARY KEY (user_id, chat_id))""")

    conn.commit()
    conn.close()


def add_authorized_user(user_id: int):
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO authorized_users (user_id) VALUES (?)", (user_id,))
    conn.commit()


def remove_authorized_user(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM authorized_users WHERE user_id = ?", (user_id,))
    conn.commit()


def is_authorized(user_id: int) -> bool:
    conn = get_conn()
    return conn.execute("SELECT 1 FROM authorized_users WHERE user_id = ?", (user_id,)).fetchone() is not None


def add_certified_user(user_id: int, chat_id: int):
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO certified_users (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id))
    conn.commit()


def remove_certified_user(user_id: int, chat_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM certified_users WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    conn.commit()


def is_certified(user_id: int, chat_id: int) -> bool:
    conn = get_conn()
    return conn.execute(
        "SELECT 1 FROM certified_users WHERE user_id = ? AND chat_id = ?", (user_id, chat_id)
    ).fetchone() is not None


def set_media_delete_time(chat_id: int, seconds: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO group_settings (chat_id, media_delete_time) VALUES (?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET media_delete_time=excluded.media_delete_time",
        (chat_id, seconds)
    )
    conn.commit()


def get_media_delete_time(chat_id: int) -> int:
    conn = get_conn()
    row = conn.execute("SELECT media_delete_time FROM group_settings WHERE chat_id=?", (chat_id,)).fetchone()
    return row["media_delete_time"] if row else 30


def save_group_title(chat_id: int, title: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO group_settings (chat_id, group_title) VALUES (?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET group_title=excluded.group_title",
        (chat_id, title)
    )
    conn.commit()


def get_group_title(chat_id: int):
    conn = get_conn()
    row = conn.execute("SELECT group_title FROM group_settings WHERE chat_id=?", (chat_id,)).fetchone()
    return row["group_title"] if row else None


def save_group_photo_id(chat_id: int, photo_id: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO group_settings (chat_id, group_photo_id) VALUES (?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET group_photo_id=excluded.group_photo_id",
        (chat_id, photo_id)
    )
    conn.commit()


def get_group_photo_id(chat_id: int):
    conn = get_conn()
    row = conn.execute("SELECT group_photo_id FROM group_settings WHERE chat_id=?", (chat_id,)).fetchone()
    return row["group_photo_id"] if row else None


def add_warn(user_id: int, chat_id: int, reason: str = "") -> int:
    conn = get_conn()
    row = conn.execute("SELECT count, reasons FROM warns WHERE user_id=? AND chat_id=?", (user_id, chat_id)).fetchone()
    if row:
        new_count = row["count"] + 1
        reasons = row["reasons"] + (f"|{reason}" if reason else "|")
        conn.execute("UPDATE warns SET count=?, reasons=? WHERE user_id=? AND chat_id=?",
                     (new_count, reasons, user_id, chat_id))
    else:
        new_count = 1
        conn.execute("INSERT INTO warns (user_id, chat_id, count, reasons) VALUES (?,?,1,?)",
                     (user_id, chat_id, reason))
    conn.commit()
    return new_count


def get_warns(user_id: int, chat_id: int):
    conn = get_conn()
    row = conn.execute("SELECT count, reasons FROM warns WHERE user_id=? AND chat_id=?", (user_id, chat_id)).fetchone()
    if not row:
        return 0, []
    reasons = [r for r in row["reasons"].split("|") if r]
    return row["count"], reasons


def remove_warn(user_id: int, chat_id: int) -> int:
    conn = get_conn()
    row = conn.execute("SELECT count, reasons FROM warns WHERE user_id=? AND chat_id=?", (user_id, chat_id)).fetchone()
    if not row or row["count"] == 0:
        return 0
    new_count = max(0, row["count"] - 1)
    reasons = row["reasons"].split("|")
    if reasons:
        reasons = reasons[:-1]
    conn.execute("UPDATE warns SET count=?, reasons=? WHERE user_id=? AND chat_id=?",
                 (new_count, "|".join(reasons), user_id, chat_id))
    conn.commit()
    return new_count


def reset_warns(user_id: int, chat_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM warns WHERE user_id=? AND chat_id=?", (user_id, chat_id))
    conn.commit()
