import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger


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
                f"🌊 **{frak('Anti-Flood Settings')}**\n\n"
                f"📊 **{frak('Current Limit:')}** {limit if limit else frak('Disabled')}\n\n"
                f"**{frak('Usage:')}** `/setflood 5` {frak('(mutes after 5 msgs in 5s)')}\n"
                f"`/setflood 0` {frak('to disable')}",
                reply_markup=markup([primary(frak("✦ /setflood 5 ✦"))])
            )
        try:
            limit = int(parts[1])
        except ValueError:
            return await message.reply(f"**{frak('Use a number.')}**")
        _set_flood_limit(message.chat.id, limit)
        if limit == 0:
            await message.reply(
                f"✅ **{frak('Anti-Flood Disabled')}**",
                reply_markup=markup([danger(frak("✦ Flood Off ✦"))])
            )
        else:
            await message.reply(
                f"✅ **{frak('Anti-Flood Set!')}**\n\n"
                f"🌊 **{frak('Limit:')}** {limit} {frak('messages per 5 seconds')}\n"
                f"⚡ **{frak('Action:')}** {frak('Mute for 1 minute')}",
                reply_markup=markup([success(frak(f"✦ Flood Limit: {limit} ✦"))])
            )

    @app.on_message(filters.command("flood") & filters.group)
    async def cmd_flood(client: Client, message: Message):
        limit = _get_flood_limit(message.chat.id)
        await message.reply(
            f"🌊 **{frak('Anti-Flood')}**\n\n"
            f"📊 **{frak('Status:')}** {f'{limit} msgs/5s' if limit else frak('Disabled')}\n\n"
            f"_{frak('Use')} `/setflood N` {frak('to configure.')}_",
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
                    f"🌊 **{frak('Flood Detected!')}**\n\n"
                    f"👤 **{frak('User:')}** {message.from_user.mention}\n"
                    f"⚡ **{frak('Action:')}** {frak('Muted for 1 minute')}\n"
                    f"📊 **{frak('Sent:')}** {entry['count']} {frak('msgs in 5s')}\n\n"
                    f"— **{frak('Powered by Madara')}** 🔥",
                    reply_markup=markup([danger(frak("✦ Flood Muted ✦"))])
                )
            except Exception:
                pass
