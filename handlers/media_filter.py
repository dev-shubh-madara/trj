import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from database import is_certified, get_media_delete_time
from utils.font import frak
from utils.buttons import markup, danger

MEDIA_FILTER = (
    filters.photo | filters.video | filters.document | filters.sticker
    | filters.animation | filters.audio | filters.voice | filters.video_note
)


def register(app: Client):

    @app.on_message(MEDIA_FILTER & filters.group, group=2)
    async def handle_media(client: Client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        if is_certified(user_id, chat_id):
            return

        delete_time = get_media_delete_time(chat_id)
        media_type = _get_media_type(message)

        try:
            warn_msg = await message.reply(
                f"⏳ **{frak('Auto-Delete Warning')}**\n\n"
                f"👤 {message.from_user.mention}\n"
                f"📁 **{frak('Type:')}** {media_type}\n"
                f"🕐 **{frak('Deleting in:')}** {delete_time} {frak('seconds')}\n\n"
                f"_{frak('Only certified members can send media.')}_",
                reply_markup=markup([danger(frak(f"Auto-deleting in {delete_time}s"))])
            )
        except Exception:
            warn_msg = None

        await asyncio.sleep(delete_time)

        try:
            await message.delete()
        except Exception:
            pass

        if warn_msg:
            try:
                await warn_msg.edit(
                    f"🔴 **{frak('Media Deleted')}**\n\n"
                    f"👤 {message.from_user.mention}'s {media_type} {frak('was removed.')}\n"
                    f"_{frak('Reason: Non-certified member sent media.')}_",
                    reply_markup=markup([danger(frak("Media Removed"))])
                )
            except Exception:
                try:
                    await warn_msg.delete()
                except Exception:
                    pass


def _get_media_type(message: Message) -> str:
    if message.photo:        return "🖼️ Image"
    if message.video:        return "🎬 Video"
    if message.document:     return "📄 File"
    if message.sticker:      return "😊 Sticker"
    if message.animation:    return "🎞️ GIF"
    if message.audio:        return "🎵 Audio"
    if message.voice:        return "🎤 Voice"
    if message.video_note:   return "📹 Video Note"
    return "📁 Media"
