from pyrogram import Client, filters
from pyrogram.types import Message
from database import is_certified
from utils.slang_words import contains_banned_word
from utils.font import frak
from utils.buttons import markup, danger


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
            f"🤖 {frak('Bot')}: `{sender.username or user_id}`"
            if is_bot
            else f"👤 {frak('User')}: {sender.mention if hasattr(sender, 'mention') else str(user_id)}"
        )

        try:
            await client.send_message(
                chat_id,
                f"⚠️ **{frak('Violation Detected & Removed')}**\n\n"
                f"{sender_label}\n"
                f"🚫 **{frak('Reason')}:** {frak('Banned/illegal content detected')}\n"
                f"📜 **{frak('Rule')}:** {frak('No slang, hate speech or illegal words')}\n\n"
                f"_{frak('Automatically deleted by GuardBot.')}_",
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
            f"🤖 {frak('Bot')}: `{sender.username or user_id}`"
            if is_bot
            else f"👤 {frak('User')}: {sender.mention if hasattr(sender, 'mention') else str(user_id)}"
        )

        try:
            await client.send_message(
                chat_id,
                f"⚠️ **{frak('Violation Detected & Removed')}**\n\n"
                f"{sender_label}\n"
                f"🚫 **{frak('Reason')}:** {frak('Caption contained banned content')}\n\n"
                f"_{frak('Automatically deleted by GuardBot.')}_",
                reply_markup=markup([danger(frak("✦ Violation Removed ✦"))])
            )
        except Exception:
            pass
