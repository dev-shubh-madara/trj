from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger


def _set_rules(chat_id, text):
    conn = get_conn()
    conn.execute(
        "INSERT INTO group_settings (chat_id, rules_text) VALUES (?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET rules_text=excluded.rules_text",
        (chat_id, text)
    )
    conn.commit()


def _get_rules(chat_id):
    conn = get_conn()
    row = conn.execute("SELECT rules_text FROM group_settings WHERE chat_id=?", (chat_id,)).fetchone()
    return row["rules_text"] if row and row["rules_text"] else None


def register(app: Client):

    @app.on_message(filters.command("setrules") & filters.group)
    async def cmd_setrules(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        parts = message.text.split(None, 1)
        if len(parts) < 2 and not message.reply_to_message:
            return await message.reply(
                f"**{frak('Usage:')}** `/setrules your rules here`\n"
                f"_{frak('Or reply to a message.')}_",
                reply_markup=markup([primary(frak("✦ /setrules text ✦"))])
            )
        text = parts[1].strip() if len(parts) > 1 else (
            message.reply_to_message.text or message.reply_to_message.caption or ""
        )
        _set_rules(message.chat.id, text)
        await message.reply(
            f"✅ **{frak('Rules Set!')}**\n\n_{frak('Members can view with')} `/rules`_",
            reply_markup=markup([success(frak("✦ Rules Saved ✦"))])
        )

    @app.on_message(filters.command("rules") & filters.group)
    async def cmd_rules(client: Client, message: Message):
        rules = _get_rules(message.chat.id)
        if not rules:
            return await message.reply(
                f"**{frak('No rules set for this group.')}**\n"
                f"_{frak('Admins can set rules with')} `/setrules`_",
                reply_markup=markup([primary(frak("✦ /setrules ✦"))])
            )
        await message.reply(
            f"📜 **{frak('Group Rules')}**\n\n{rules}\n\n"
            f"— **{frak('Powered by Madara')}** 🔥",
            reply_markup=markup([primary(frak("✦ Read & Follow ✦"))])
        )

    @app.on_message(filters.command("resetrules") & filters.group)
    async def cmd_resetrules(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        conn = get_conn()
        conn.execute(
            "UPDATE group_settings SET rules_text=NULL WHERE chat_id=?", (message.chat.id,)
        )
        conn.commit()
        await message.reply(
            f"🗑️ **{frak('Rules Reset')}**",
            reply_markup=markup([danger(frak("✦ Rules Cleared ✦"))])
        )
