from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from database import is_certified
from utils.slang_words import contains_banned_word
from utils.font import frak
from utils.buttons import markup, danger
from utils.emojis import em, em_row

PM = ParseMode.HTML


def register(app: Client):

    @app.on_message(filters.text & filters.group, group=1)
    async def handle_text(client: Client, message: Message):
        sender = message.from_user or message.sender_chat
        if not sender:
            return

        chat_id = message.chat.id
        user_id = getattr(sender, "id", None)
        is_bot = getattr(sender, "is_bot", False)

        if not is_bot and user_id and is_certified(user_id, chat_id):
            return

        text = message.text or ""
        if not contains_banned_word(text):
            return

        try:
            await message.delete()
        except Exception:
            pass

        sender_label = (
            f"🤖 <b>{frak('Bot:')}</b> <code>{sender.username or user_id}</code>"
            if is_bot
            else f"👤 <b>{frak('User:')}</b> {sender.mention if hasattr(sender, 'mention') else str(user_id)}"
        )

        try:
            await client.send_message(
                chat_id,
                f"{em_row(3)}\n\n"
                f"⚠️ <b>{frak('Violation Detected & Removed!')}</b>\n\n"
                f"{em()} {sender_label}\n"
                f"{em()} 🚫 <b>{frak('Reason:')}</b> {frak('Banned/illegal content detected')}\n"
                f"{em()} 📜 <b>{frak('Rule:')}</b> {frak('No slang, hate speech or illegal words')}\n\n"
                f"<i>🤖 {frak('Automatically deleted by GuardBot.')}</i>\n\n"
                f"— <b>{frak('Powered by Madara')}</b> 🔥",
                parse_mode=PM,
                reply_markup=markup([danger(frak("✦ Violation Removed ✦"))])
            )
        except Exception:
            pass

    @app.on_message(filters.caption & filters.group, group=1)
    async def handle_caption(client: Client, message: Message):
        sender = message.from_user or message.sender_chat
        if not sender:
            return

        chat_id = message.chat.id
        user_id = getattr(sender, "id", None)
        is_bot = getattr(sender, "is_bot", False)

        if not is_bot and user_id and is_certified(user_id, chat_id):
            return

        caption = message.caption or ""
        if not contains_banned_word(caption):
            return

        try:
            await message.delete()
        except Exception:
            pass

        sender_label = (
            f"🤖 <b>{frak('Bot:')}</b> <code>{sender.username or user_id}</code>"
            if is_bot
            else f"👤 <b>{frak('User:')}</b> {sender.mention if hasattr(sender, 'mention') else str(user_id)}"
        )

        try:
            await client.send_message(
                chat_id,
                f"{em_row(3)}\n\n"
                f"⚠️ <b>{frak('Caption Violation Removed!')}</b>\n\n"
                f"{em()} {sender_label}\n"
                f"{em()} 🚫 <b>{frak('Reason:')}</b> {frak('Caption contained banned content')}\n\n"
                f"<i>🤖 {frak('Automatically deleted by GuardBot.')}</i>\n\n"
                f"— <b>{frak('Powered by Madara')}</b> 🔥",
                parse_mode=PM,
                reply_markup=markup([danger(frak("✦ Violation Removed ✦"))])
            )
        except Exception:
            pass
