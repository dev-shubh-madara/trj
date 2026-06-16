from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, em_row

PM = ParseMode.HTML


def _add_filter(chat_id, keyword, response):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_filters (chat_id, keyword, response) VALUES (?,?,?) "
        "ON CONFLICT(chat_id, keyword) DO UPDATE SET response=excluded.response",
        (chat_id, keyword.lower(), response)
    )
    conn.commit()


def _remove_filter(chat_id, keyword):
    conn = get_conn()
    conn.execute("DELETE FROM chat_filters WHERE chat_id=? AND keyword=?", (chat_id, keyword.lower()))
    conn.commit()


def _list_filters(chat_id):
    conn = get_conn()
    return conn.execute(
        "SELECT keyword FROM chat_filters WHERE chat_id=? ORDER BY keyword", (chat_id,)
    ).fetchall()


def _match_filter(chat_id, text):
    conn = get_conn()
    rows = conn.execute(
        "SELECT keyword, response FROM chat_filters WHERE chat_id=?", (chat_id,)
    ).fetchall()
    text_lower = text.lower()
    for row in rows:
        if row["keyword"] in text_lower:
            return row["response"]
    return None


def register(app: Client):

    @app.on_message(filters.command("filter") & filters.group)
    async def cmd_filter(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        parts = message.text.split(None, 2)
        if len(parts) < 3 and not message.reply_to_message:
            return await message.reply(
                f"{em()} <b>{frak('Usage:')}</b> <code>/filter keyword response</code>\n"
                f"{em()} <i>{frak('Or reply to a message:')}</i> <code>/filter keyword</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("✦ /filter word reply ✦"))])
            )
        keyword = parts[1].lower()
        if len(parts) >= 3:
            response = parts[2]
        elif message.reply_to_message:
            response = message.reply_to_message.text or message.reply_to_message.caption or ""
        else:
            return await message.reply(
                f"{em()} <b>{frak('Provide a response.')}</b>",
                parse_mode=PM
            )

        _add_filter(message.chat.id, keyword, response)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"✅ <b>{frak('Filter Added!')}</b>\n\n"
            f"{em()} 🔑 <b>{frak('Keyword:')}</b> <code>{keyword}</code>\n"
            f"{em()} 💬 <b>{frak('Response:')}</b> {response[:80]}{'...' if len(response) > 80 else ''}\n\n"
            f"<i>{frak('Auto-reply will trigger when the keyword is detected.')}</i>",
            parse_mode=PM,
            reply_markup=markup([success(frak(f"✦ Filter: {keyword[:20]} ✦"))])
        )

    @app.on_message(filters.command("stop") & filters.group)
    async def cmd_stop(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply(
                f"{em()} <b>{frak('Usage:')}</b> <code>/stop keyword</code>",
                parse_mode=PM
            )
        keyword = parts[1].lower()
        _remove_filter(message.chat.id, keyword)
        await message.reply(
            f"{em()} 🗑️ <b>{frak('Filter Removed')}</b>\n"
            f"{em()} <code>{keyword}</code>",
            parse_mode=PM,
            reply_markup=markup([danger(frak(f"✦ {keyword} Removed ✦"))])
        )

    @app.on_message(filters.command("filters") & filters.group)
    async def cmd_filters(client: Client, message: Message):
        rows = _list_filters(message.chat.id)
        if not rows:
            return await message.reply(
                f"{em()} <b>{frak('No filters set in this group.')}</b>\n"
                f"<i>{frak('Use /filter keyword reply to add one.')}</i>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("✦ /filter word reply ✦"))])
            )
        lines = "\n".join(f"{em()} <code>{r['keyword']}</code>" for r in rows)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"🔍 <b>{frak('Active Filters')}</b> ({len(rows)}):\n\n"
            f"{lines}",
            parse_mode=PM,
            reply_markup=markup([success(frak(f"✦ {len(rows)} Filters ✦"))])
        )

    @app.on_message(filters.command("stopall") & filters.group)
    async def cmd_stopall(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        conn = get_conn()
        conn.execute("DELETE FROM chat_filters WHERE chat_id=?", (message.chat.id,))
        conn.commit()
        await message.reply(
            f"{em()} 🗑️ <b>{frak('All Filters Cleared')}</b>",
            parse_mode=PM,
            reply_markup=markup([danger(frak("✦ All Filters Removed ✦"))])
        )

    @app.on_message(filters.text & filters.group, group=4)
    async def auto_filter(client: Client, message: Message):
        if not message.text or message.text.startswith("/"):
            return
        response = _match_filter(message.chat.id, message.text)
        if response:
            await message.reply(response, parse_mode=PM)
