from pyrogram import Client, filters
from pyrogram.types import Message
from database import is_certified
from utils.slang_words import contains_banned_word
from utils.font import frak
from utils.buttons import markup, danger


def register(app: Client):

    @app.on_message(filters.text & filters.group, group=1)
    async def handle_text(client: Client, message: Message):
        if not message.from_user:
            return
        chat_id = message.chat.id
        user_id = message.from_user.id
        if is_certified(user_id, chat_id):
            return
        text = message.text or ""
        if not contains_banned_word(text):
            return
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await client.send_message(
                chat_id,
                f"⚠️ **{frak('Violation Detected & Removed')}**\n\n"
                f"👤 **{frak('User:')}** {message.from_user.mention}\n"
                f"🚫 **{frak('Reason:')}** {frak('Message contained banned/illegal content')}\n"
                f"📜 **{frak('Rule:')}** {frak('No slang, hate speech, or illegal words allowed')}\n\n"
                f"_{frak('This message was automatically deleted by GuardBot.')}_",
                reply_markup=markup([danger(frak("Violation Removed"))])
            )
        except Exception:
            pass

    @app.on_message(filters.caption & filters.group, group=1)
    async def handle_caption(client: Client, message: Message):
        if not message.from_user:
            return
        chat_id = message.chat.id
        user_id = message.from_user.id
        if is_certified(user_id, chat_id):
            return
        caption = message.caption or ""
        if not contains_banned_word(caption):
            return
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await client.send_message(
                chat_id,
                f"⚠️ **{frak('Violation Detected & Removed')}**\n\n"
                f"👤 **{frak('User:')}** {message.from_user.mention}\n"
                f"🚫 **{frak('Reason:')}** {frak('Caption contained banned/illegal content')}\n\n"
                f"_{frak('Automatically deleted by GuardBot.')}_",
                reply_markup=markup([danger(frak("Violation Removed"))])
            )
        except Exception:
            pass
