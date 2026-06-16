from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from config import OWNER_ID, ALLOWED_MEDIA_TIMES
from database import (
    set_media_delete_time, get_media_delete_time, get_group_title,
    get_group_photo_id, is_authorized, get_conn
)
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default
from utils.emojis import em, em_row

PM = ParseMode.HTML


def register(app: Client):

    @app.on_message(filters.command("setgrouppic") & filters.group)
    async def cmd_set_group_pic(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            await message.reply(
                f"{em()} ⛔ <b>{frak('Not Authorized')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        chat_member = await client.get_chat_member(chat_id, user.id)
        if chat_member.status.value not in ("owner", "administrator"):
            await message.reply(
                f"{em()} ⛔ <b>{frak('Admins Only')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Admins Only"))])
            )
            return

        parts = message.text.split()
        if len(parts) < 2:
            current = get_media_delete_time(chat_id)
            await message.reply(
                f"{em_row(4)}\n\n"
                f"⏱️ <b>{frak('Media Auto-Delete Timer')}</b>\n\n"
                f"{em()} <b>{frak('Usage:')}</b> <code>/setgrouppic &lt;time&gt;</code>\n"
                f"{em()} <b>{frak('Allowed times:')}</b> <code>10</code>, <code>20</code>, <code>30</code> {frak('seconds')}\n"
                f"{em()} <b>{frak('Current setting:')}</b> <code>{current}s</code>\n\n"
                f"<i>{frak('Example:')} /setgrouppic 10</i>",
                parse_mode=PM,
                reply_markup=markup(
                    [primary(frak("10s")), primary(frak("20s")), primary(frak("30s"))]
                )
            )
            return

        try:
            seconds = int(parts[1])
        except ValueError:
            await message.reply(
                f"{em()} <b>{frak('Invalid time. Use 10, 20, or 30.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Invalid Time"))])
            )
            return

        if seconds not in ALLOWED_MEDIA_TIMES:
            await message.reply(
                f"{em()} <b>{frak('Choose from: 10, 20, or 30 seconds.')}</b>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("10s")), primary(frak("20s")), primary(frak("30s"))])
            )
            return

        set_media_delete_time(chat_id, seconds)
        await message.reply(
            f"{em_row(5)}\n\n"
            f"✅ <b>{frak('Media Auto-Delete Timer Updated!')}</b>\n\n"
            f"{em()} <b>{frak('New Time:')}</b> <code>{seconds}s</code>\n"
            f"{em()} <b>{frak('Effect:')}</b> {frak('Non-certified media deleted after')} <code>{seconds}s</code>\n"
            f"{em()} <b>{frak('Certified members:')}</b> {frak('Exempt from this rule')}\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup([success(frak(f"Timer: {seconds}s"))])
        )

    @app.on_message(filters.command("groupinfo") & filters.group)
    async def cmd_group_info(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            return

        conn = get_conn()
        certified_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM certified_users WHERE chat_id = ?", (chat_id,)
        ).fetchone()["cnt"]

        warn_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM warns WHERE chat_id = ?", (chat_id,)
        ).fetchone()["cnt"] if conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='warns'"
        ).fetchone() else 0

        notes_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM notes WHERE chat_id = ?", (chat_id,)
        ).fetchone()["cnt"]

        media_time = get_media_delete_time(chat_id)
        title = get_group_title(chat_id) or frak("Not saved")
        photo = get_group_photo_id(chat_id)

        flood_row = conn.execute(
            "SELECT flood_limit FROM group_settings WHERE chat_id=?", (chat_id,)
        ).fetchone()
        flood = flood_row["flood_limit"] if flood_row and flood_row["flood_limit"] else 0

        rules_row = conn.execute(
            "SELECT rules_text FROM group_settings WHERE chat_id=?", (chat_id,)
        ).fetchone()
        has_rules = bool(rules_row and rules_row["rules_text"])

        await message.reply(
            f"{em_row(6)}\n\n"
            f"📊 <b>{frak('Group Protection Dashboard')}</b>\n\n"
            f"{em()} <b>{frak('Group:')}</b> <code>{message.chat.title}</code>\n"
            f"{em()} <b>{frak('Chat ID:')}</b> <code>{chat_id}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"⚙️ <b>{frak('Settings:')}</b>\n"
            f"{em()} ⏱️ {frak('Media auto-delete:')} <code>{media_time}s</code>\n"
            f"{em()} 📝 {frak('Protected title:')} <code>{title}</code>\n"
            f"{em()} 🖼️ {frak('Protected photo:')} {'✅' if photo else '❌'}\n"
            f"{em()} ⭐ {frak('Certified members:')} <code>{certified_count}</code>\n"
            f"{em()} 📋 {frak('Saved notes:')} <code>{notes_count}</code>\n"
            f"{em()} ⚠️ {frak('Active warns:')} <code>{warn_count}</code>\n"
            f"{em()} 🌊 {frak('Flood limit:')} <code>{f'{flood} msgs/5s' if flood else 'Disabled'}</code>\n"
            f"{em()} 📜 {frak('Rules set:')} {'✅' if has_rules else '❌'}\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🛡️ <b>{frak('Active Protections:')}</b>\n"
            f"{em()} ✅ {frak('Slang/illegal word filter')}\n"
            f"{em()} ✅ {frak('Media auto-delete (non-certified)')}\n"
            f"{em()} ✅ {frak('Group name protection')}\n"
            f"{em()} ✅ {frak('Group photo protection')}\n"
            f"{em()} ✅ {'🌊 Anti-flood' if flood else '❌ Anti-flood (set /setflood)'}\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup(
                [primary(frak("Dashboard")), success(frak("All Systems Active ✅"))]
            )
        )
