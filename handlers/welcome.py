import asyncio
import os
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus

from database import is_certified, get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default


def _get_welcome_settings(chat_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT welcome_text, welcome_enabled FROM group_settings WHERE chat_id = ?",
        (chat_id,)
    ).fetchone()
    if not row:
        return None, True
    return row["welcome_text"], bool(row["welcome_enabled"])


def _set_welcome_text(chat_id: int, text: str):
    conn = get_conn()
    conn.execute(
        """INSERT INTO group_settings (chat_id, welcome_text, welcome_enabled)
           VALUES (?, ?, 1)
           ON CONFLICT(chat_id) DO UPDATE SET
               welcome_text = excluded.welcome_text,
               welcome_enabled = 1""",
        (chat_id, text)
    )
    conn.commit()


def _set_welcome_enabled(chat_id: int, enabled: bool):
    conn = get_conn()
    conn.execute(
        """INSERT INTO group_settings (chat_id, welcome_enabled)
           VALUES (?, ?)
           ON CONFLICT(chat_id) DO UPDATE SET welcome_enabled = excluded.welcome_enabled""",
        (chat_id, int(enabled))
    )
    conn.commit()


DEFAULT_WELCOME = (
    "👋 **{frak_welcome}, {name}!**\n\n"
    "🎉 {frak_joined} **{chat}**\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📋 **{frak_rules}:**\n"
    "• 🚫 {frak_no_slang}\n"
    "• 🚫 {frak_no_illegal}\n"
    "• 🚫 {frak_no_spam}\n"
    "• ✅ {frak_be_respectful}\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "🛡️ _{frak_protected}_"
)


def register(app: Client):

    @app.on_chat_member_updated(filters.group)
    async def on_member_join(client: Client, update: ChatMemberUpdated):
        if not update.new_chat_member:
            return
        new_status = update.new_chat_member.status
        if new_status not in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
            return
        old_status = update.old_chat_member.status if update.old_chat_member else None
        if old_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return

        chat_id = update.chat.id
        user = update.new_chat_member.user
        if user.is_bot:
            return

        welcome_text, enabled = _get_welcome_settings(chat_id)
        if not enabled:
            return

        name = user.first_name or "Member"
        chat_title = update.chat.title or "the group"
        mention = user.mention

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
                f"🛡️ _{frak('This group is protected by GuardBot')}_"
            )

        pfp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                pfp_path = tmp.name
            downloaded = await client.download_media(
                user.photo.big_file_id if user.photo else None,
                file_name=pfp_path
            ) if user.photo else None
            if not downloaded:
                pfp_path = None
        except Exception:
            pfp_path = None

        reply_markup = markup(
            [
                success(frak("✦ Welcome ✦"), data="noop"),
                primary(frak(f"✦ {chat_title} ✦"), data="noop")
            ],
            [
                danger(frak("✦ Read Rules ✦"), data="noop"),
                primary(frak("✦ Certified? ✦"), data="noop")
            ]
        )

        try:
            if pfp_path and os.path.exists(pfp_path):
                await client.send_photo(
                    chat_id,
                    photo=pfp_path,
                    caption=text,
                    reply_markup=reply_markup
                )
            else:
                await client.send_message(
                    chat_id,
                    text,
                    reply_markup=reply_markup
                )
        except Exception:
            pass
        finally:
            if pfp_path and os.path.exists(pfp_path):
                try:
                    os.unlink(pfp_path)
                except Exception:
                    pass

    @app.on_message(filters.command("setwelcome") & filters.group)
    async def cmd_set_welcome(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        user = message.from_user
        if user.id != OWNER_ID and not is_authorized(user.id):
            return

        parts = message.text.split(None, 1)
        if len(parts) < 2 or parts[1].strip().lower() == "off":
            _set_welcome_enabled(message.chat.id, False)
            await message.reply(
                f"🔕 **{frak('Welcome Messages Disabled')}**\n\n"
                f"_{frak('New members will not receive a welcome message.')}_\n\n"
                f"_{frak('Use')} `/setwelcome <text>` {frak('to re-enable with custom text.')}_",
                reply_markup=markup([danger(frak("✦ Welcome Off ✦"))])
            )
            return

        custom_text = parts[1].strip()
        _set_welcome_text(message.chat.id, custom_text)
        await message.reply(
            f"✅ **{frak('Welcome Message Set!')}**\n\n"
            f"📝 **{frak('Preview')}:**\n\n{custom_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"_{frak('Variables you can use')}:_\n"
            f"• `{{name}}` — {frak('User mention')}\n"
            f"• `{{first}}` — {frak('First name')}\n"
            f"• `{{last}}` — {frak('Last name')}\n"
            f"• `{{chat}}` — {frak('Group name')}\n"
            f"• `{{id}}` — {frak('User ID')}",
            reply_markup=markup(
                [success(frak("✦ Welcome Set ✦")), primary(frak("✦ With Photo ✦"))]
            )
        )

    @app.on_message(filters.command("welcome") & filters.group)
    async def cmd_welcome_info(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        user = message.from_user
        if user.id != OWNER_ID and not is_authorized(user.id):
            return

        welcome_text, enabled = _get_welcome_settings(message.chat.id)
        status = frak("Enabled ✅") if enabled else frak("Disabled 🔕")
        preview = welcome_text or frak("Using default welcome message")

        await message.reply(
            f"👋 **{frak('Welcome System Info')}**\n\n"
            f"🔘 **{frak('Status')}:** {status}\n\n"
            f"📝 **{frak('Current Message')}:**\n{preview}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"• `/setwelcome <text>` — {frak('Set custom welcome')}\n"
            f"• `/setwelcome off` — {frak('Disable welcome')}",
            reply_markup=markup(
                [success(frak("✦ Enabled ✦")) if enabled else danger(frak("✦ Disabled ✦")),
                 primary(frak("✦ Use /setwelcome ✦"))]
            )
        )
