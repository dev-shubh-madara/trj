import os
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus, ParseMode

from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, ems, em_row

PM = ParseMode.HTML
MADARA = f"\n\n— <b>{frak('Powered by Madara')}</b> 🔥"


def _get_welcome(chat_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT welcome_text, welcome_enabled FROM group_settings WHERE chat_id=?",
        (chat_id,)
    ).fetchone()
    if not row:
        return None, True
    enabled = row["welcome_enabled"]
    return row["welcome_text"], bool(enabled if enabled is not None else 1)


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


async def _do_welcome(client: Client, chat_id: int, chat_title: str, user):
    welcome_text, enabled = _get_welcome(chat_id)
    if not enabled:
        return

    name = user.first_name or "Member"
    mention = f'<a href="tg://user?id={user.id}">{name}</a>'
    chat_name = chat_title or "the group"

    if welcome_text:
        text = (welcome_text
                .replace("{name}", mention)
                .replace("{first}", user.first_name or name)
                .replace("{last}", user.last_name or "")
                .replace("{chat}", chat_name)
                .replace("{id}", str(user.id)))
    else:
        text = (
            f"{em_row(6)}\n\n"
            f"👋 <b>{frak('Welcome')}</b>, {mention}!\n\n"
            f"{em()} {frak('You have joined')} <b>{chat_name}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 <b>{frak('Group Rules:')}</b>\n"
            f"{em()} 🚫 {frak('No slang or hate speech')}\n"
            f"{em()} 🚫 {frak('No illegal content or media')}\n"
            f"{em()} 🚫 {frak('No spam or flooding')}\n"
            f"{em()} ✅ {frak('Be respectful to everyone')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{em_row(6)}\n\n"
            f"🛡️ <i>{frak('This group is protected by GuardBot')}</i>"
            f"{MADARA}"
        )

    kb = markup(
        [success(frak("✦ Welcome ✦")),  primary(frak("✦ /rules ✦"))],
        [danger( frak("✦ No Slang ✦")), success(frak("✦ Be Respectful ✦"))]
    )

    pfp_path = None
    downloaded = False
    try:
        if user.photo:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                pfp_path = tmp.name
            result = await client.download_media(user.photo.big_file_id, file_name=pfp_path)
            if result and os.path.exists(pfp_path) and os.path.getsize(pfp_path) > 1024:
                downloaded = True
    except Exception:
        downloaded = False

    try:
        if downloaded and pfp_path:
            await client.send_photo(
                chat_id,
                photo=pfp_path,
                caption=text,
                has_spoiler=True,
                parse_mode=PM,
                reply_markup=kb
            )
        else:
            await client.send_message(chat_id, text, parse_mode=PM, reply_markup=kb)
    except Exception:
        try:
            await client.send_message(chat_id, text, parse_mode=PM, reply_markup=kb)
        except Exception:
            pass
    finally:
        if pfp_path and os.path.exists(pfp_path):
            try:
                os.unlink(pfp_path)
            except Exception:
                pass


def register(app: Client):

    @app.on_message(filters.new_chat_members & filters.group, group=2)
    async def welcome_regular(client: Client, message: Message):
        for user in message.new_chat_members:
            if user.is_bot:
                continue
            await _do_welcome(client, message.chat.id, message.chat.title, user)

    @app.on_chat_member_updated()
    async def welcome_supergroup(client: Client, update: ChatMemberUpdated):
        if update.chat is None:
            return
        if update.chat.type.value not in ("group", "supergroup"):
            return
        if not update.new_chat_member:
            return

        new_s = update.new_chat_member.status
        old_s = update.old_chat_member.status if update.old_chat_member else None

        joined = (
            new_s in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR)
            and old_s in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, None)
        )
        if not joined:
            return

        user = update.new_chat_member.user
        if user.is_bot:
            return
        await _do_welcome(client, update.chat.id, update.chat.title, user)

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
                f"{em()} <b>{frak('Welcome Messages Disabled')}</b>\n"
                f"<i>{frak('Use /setwelcome text to re-enable.')}</i>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("✦ Welcome Off ✦"))])
            )

        _save_welcome(message.chat.id, parts[1].strip())
        await message.reply(
            f"{em()} <b>{frak('Welcome Message Set!')}</b>\n\n"
            f"📝 <b>{frak('Variables you can use:')}</b>\n"
            f"• <code>{{name}}</code> — {frak('user mention')}\n"
            f"• <code>{{first}}</code> — {frak('first name')}\n"
            f"• <code>{{chat}}</code> — {frak('group name')}\n"
            f"• <code>{{id}}</code> — {frak('user ID')}\n\n"
            f"<i>{frak('Profile photo is sent as spoiler automatically.')}</i>",
            parse_mode=PM,
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
            f"{em()} <b>{frak('Welcome System')}</b>\n\n"
            f"{em()} <b>{frak('Status:')}</b> {frak('Enabled ✅') if en else frak('Disabled 🔕')}\n\n"
            f"📝 {wt or frak('Default message (spoiler profile photo)')}",
            parse_mode=PM,
            reply_markup=markup(
                [success(frak("✦ On ✦")) if en else danger(frak("✦ Off ✦")),
                 primary(frak("✦ /setwelcome ✦"))]
            )
        )
