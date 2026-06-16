import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ParseMode
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, em_row

PM = ParseMode.HTML


def _get_flood_limit(chat_id):
    conn = get_conn()
    row = conn.execute("SELECT flood_limit FROM group_settings WHERE chat_id=?", (chat_id,)).fetchone()
    return row["flood_limit"] if row and row["flood_limit"] else 0


def _set_flood_limit(chat_id, limit):
    conn = get_conn()
    conn.execute(
        "INSERT INTO group_settings (chat_id, flood_limit) VALUES (?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET flood_limit=excluded.flood_limit",
        (chat_id, limit)
    )
    conn.commit()


_flood_cache = {}


def register(app: Client):

    @app.on_message(filters.command("setflood") & filters.group)
    async def cmd_setflood(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        parts = message.text.split()
        if len(parts) < 2:
            limit = _get_flood_limit(message.chat.id)
            return await message.reply(
                f"{em_row(4)}\n\n"
                f"🌊 <b>{frak('Anti-Flood Settings')}</b>\n\n"
                f"{em()} <b>{frak('Status:')}</b> {'🟢 ' + str(limit) + ' msgs/5s' if limit else '🔴 Disabled'}\n\n"
                f"{em()} <b>{frak('Usage:')}</b> <code>/setflood 5</code> {frak('(mutes after 5 msgs in 5s)')}\n"
                f"{em()} <code>/setflood 0</code> {frak('to disable')}",
                parse_mode=PM,
                reply_markup=markup([primary(frak("✦ /setflood 5 ✦"))])
            )
        try:
            limit = int(parts[1])
        except ValueError:
            return await message.reply(
                f"{em()} <b>{frak('Use a number.')}</b>",
                parse_mode=PM
            )
        _set_flood_limit(message.chat.id, limit)
        if limit == 0:
            await message.reply(
                f"{em()} ✅ <b>{frak('Anti-Flood Disabled')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("✦ Flood Off ✦"))])
            )
        else:
            await message.reply(
                f"{em_row(4)}\n\n"
                f"✅ <b>{frak('Anti-Flood Enabled!')}</b>\n\n"
                f"{em()} 🌊 <b>{frak('Limit:')}</b> <code>{limit}</code> {frak('messages per 5 seconds')}\n"
                f"{em()} ⚡ <b>{frak('Action:')}</b> {frak('Mute for 1 minute')}\n\n"
                f"— <b>{frak('Powered by Madara')}</b> 🔥",
                parse_mode=PM,
                reply_markup=markup([success(frak(f"✦ Flood Limit: {limit} ✦"))])
            )

    @app.on_message(filters.command("flood") & filters.group)
    async def cmd_flood(client: Client, message: Message):
        limit = _get_flood_limit(message.chat.id)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"🌊 <b>{frak('Anti-Flood Status')}</b>\n\n"
            f"{em()} <b>{frak('Status:')}</b> {f'🟢 {limit} msgs/5s' if limit else '🔴 Disabled'}\n\n"
            f"<i>{frak('Use')} /setflood N {frak('to configure.')}</i>",
            parse_mode=PM,
            reply_markup=markup(
                [success(frak("✦ Active ✦")) if limit else danger(frak("✦ Disabled ✦")),
                 primary(frak("✦ /setflood ✦"))]
            )
        )

    @app.on_message(filters.group & filters.text, group=5)
    async def flood_check(client: Client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        limit = _get_flood_limit(chat_id)
        if not limit:
            return

        from database import is_certified
        from config import OWNER_ID
        uid = message.from_user.id
        if uid == OWNER_ID or is_certified(uid, chat_id):
            return

        key = (chat_id, uid)
        now = time.time()

        if key not in _flood_cache:
            _flood_cache[key] = {"count": 0, "window_start": now}

        entry = _flood_cache[key]
        if now - entry["window_start"] > 5:
            entry["count"] = 1
            entry["window_start"] = now
        else:
            entry["count"] += 1

        if entry["count"] >= limit:
            _flood_cache[key] = {"count": 0, "window_start": now}
            from datetime import datetime, timedelta
            until = datetime.now() + timedelta(minutes=1)
            try:
                await client.restrict_chat_member(
                    chat_id, uid,
                    ChatPermissions(can_send_messages=False),
                    until_date=until
                )
                await client.send_message(
                    chat_id,
                    f"{em_row(4)}\n\n"
                    f"🌊 <b>{frak('Flood Detected!')}</b>\n\n"
                    f"{em()} <b>{frak('User:')}</b> {message.from_user.mention}\n"
                    f"{em()} ⚡ <b>{frak('Action:')}</b> {frak('Muted for 1 minute')}\n"
                    f"{em()} 📊 <b>{frak('Sent:')}</b> <code>{entry['count']}</code> {frak('msgs in 5s')}\n\n"
                    f"— <b>{frak('Powered by Madara')}</b> 🔥",
                    parse_mode=PM,
                    reply_markup=markup([danger(frak("✦ Flood Muted ✦"))])
                )
            except Exception:
                pass
