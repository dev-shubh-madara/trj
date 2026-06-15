import os
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus

from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger


def _get_welcome(chat_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT welcome_text, welcome_enabled FROM group_settings WHERE chat_id=?",
        (chat_id,)
    ).fetchone()
    if not row:
        return None, True
    return row["welcome_text"], bool(row["welcome_enabled"] if row["welcome_enabled"] is not None else 1)


def _save_welcome(chat_id, text):
    conn = get_conn()
    conn.execute(
        "INSERT INTO group_settings (chat_id, welcome_text, welcome_enabled) VALUES (?,?,1) "
        "ON CONFLICT(chat_id) DO UPDATE SET welcome_text=excluded.welcome_text, welcome_enabled=1",
        (chat_id, text)
    )
    conn.commit()


def _toggle_welcome(chat_id, enabled):
    conn = get_conn()
    conn.execute(
        "INSERT INTO group_settings (chat_id, welcome_enabled) VALUES (?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET welcome_enabled=excluded.welcome_enabled",
        (chat_id, int(enabled))
    )
    conn.commit()


def register(app: Client):

    @app.on_chat_member_updated()
    async def on_new_member(client: Client, update: ChatMemberUpdated):
        if update.chat is None:
            return
        if update.chat.type.value not in ("group", "supergroup"):
            return
        if not update.new_chat_member:
            return

        new_status = update.new_chat_member.status
        old_status = update.old_chat_member.status if update.old_chat_member else None

        joined = (
            new_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR)
            and old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, None)
        )
        if not joined:
            return

        user = update.new_chat_member.user
        if user.is_bot:
            return

        chat_id = update.chat.id
        welcome_text, enabled = _get_welcome(chat_id)
        if not enabled:
            return

        name = user.first_name or "Member"
        mention = user.mention
        chat_title = update.chat.title or "the group"

        if welcome_text:
            text = (welcome_text
                    .replace("{name}", mention)
                    .replace("{first}", user.first_name or name)
                    .replace("{last}", user.last_name or "")
                    .replace("{chat}", chat_title)
                    .replace("{id}", str(user.id)))
        else:
            text = (
                f"👋 **{frak('Welcome')}, {mention}!**\n\n"
                f"🎉 {frak('You just joined')} **{chat_title}**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 **{frak('Group Rules')}:**\n"
                f"• 🚫 {frak('No slang or hate speech')}\n"
                f"• 🚫 {frak('No illegal content or media')}\n"
                f"• 🚫 {frak('No spam or flooding')}\n"
                f"• ✅ {frak('Be respectful to everyone')}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🛡️ _{frak('This group is protected by GuardBot')}_\n\n"
                f"— **{frak('Powered by Madara')}** 🔥"
            )

        pfp_path = None
        try:
            if user.photo:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    pfp_path = tmp.name
                await client.download_media(user.photo.big_file_id, file_name=pfp_path)
        except Exception:
            pfp_path = None

        kb = markup(
            [success(frak("✦ Welcome ✦")), primary(frak(f"✦ {chat_title[:15]} ✦"))],
            [danger(frak("✦ Read Rules ✦")), primary(frak("✦ Get Certified ✦"))]
        )

        try:
            if pfp_path and os.path.exists(pfp_path) and os.path.getsize(pfp_path) > 0:
                await client.send_photo(chat_id, photo=pfp_path, caption=text, reply_markup=kb)
            else:
                await client.send_message(chat_id, text, reply_markup=kb)
        except Exception:
            try:
                await client.send_message(chat_id, text, reply_markup=kb)
            except Exception:
                pass
        finally:
            if pfp_path and os.path.exists(pfp_path):
                try:
                    os.unlink(pfp_path)
                except Exception:
                    pass

    @app.on_message(filters.command("setwelcome") & filters.group)
    async def cmd_setwelcome(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        if message.from_user.id != OWNER_ID and not is_authorized(message.from_user.id):
            return

        parts = message.text.split(None, 1)
        if len(parts) < 2 or parts[1].strip().lower() == "off":
            _toggle_welcome(message.chat.id, False)
            return await message.reply(
                f"🔕 **{frak('Welcome Messages Disabled')}**\n"
                f"_{frak('Use /setwelcome text to re-enable.')}_",
                reply_markup=markup([danger(frak("✦ Welcome Off ✦"))])
            )

        _save_welcome(message.chat.id, parts[1].strip())
        await message.reply(
            f"✅ **{frak('Welcome Message Set!')}**\n\n"
            f"📝 **{frak('Variables:')}**\n"
            f"• `{{name}}` {frak('mention')} • `{{first}}` {frak('first name')}\n"
            f"• `{{chat}}` {frak('group')} • `{{id}}` {frak('user id')}",
            reply_markup=markup([success(frak("✦ Welcome Set ✦"))])
        )

    @app.on_message(filters.command("welcome") & filters.group)
    async def cmd_welcome(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        if message.from_user.id != OWNER_ID and not is_authorized(message.from_user.id):
            return
        wt, en = _get_welcome(message.chat.id)
        await message.reply(
            f"👋 **{frak('Welcome Status')}**\n\n"
            f"🔘 {frak('Enabled') if en else frak('Disabled')}\n\n"
            f"📝 {wt or frak('Using default message')}",
            reply_markup=markup(
                [success(frak("✦ On ✦")) if en else danger(frak("✦ Off ✦")),
                 primary(frak("✦ /setwelcome ✦"))]
            )
        )
