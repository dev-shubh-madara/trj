from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID, ALLOWED_MEDIA_TIMES
from database import (
    set_media_delete_time, get_media_delete_time, get_group_title,
    get_group_photo_id, is_authorized, get_conn
)
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default


def register(app: Client):

    @app.on_message(filters.command("setgrouppic") & filters.group)
    async def cmd_set_group_pic(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            await message.reply(
                f"⛔ **{frak('Not Authorized')}**",
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        chat_member = await client.get_chat_member(chat_id, user.id)
        if chat_member.status.value not in ("owner", "administrator"):
            await message.reply(
                f"⛔ **{frak('You must be a group admin to use this command.')}**",
                reply_markup=markup([danger(frak("Admins Only"))])
            )
            return

        parts = message.text.split()
        if len(parts) < 2:
            current = get_media_delete_time(chat_id)
            await message.reply(
                f"❓ **{frak('Usage:')}** `/setgrouppic <time>`\n\n"
                f"⏱️ **{frak('Allowed times:')}** `10`, `20`, `30` {frak('seconds')}\n"
                f"📌 **{frak('Current setting:')}** `{current}` {frak('seconds')}\n\n"
                f"{frak('Example:')} `/setgrouppic 10`",
                reply_markup=markup(
                    [primary(frak("10s")), primary(frak("20s")), primary(frak("30s"))]
                )
            )
            return

        try:
            seconds = int(parts[1])
        except ValueError:
            await message.reply(
                f"❌ **{frak('Invalid time.')}** {frak('Please use')} `10`, `20`, {frak('or')} `30`.",
                reply_markup=markup([danger(frak("Invalid Time"))])
            )
            return

        if seconds not in ALLOWED_MEDIA_TIMES:
            await message.reply(
                f"❌ **{frak('Invalid time.')}** {frak('Choose from:')} `10`, `20`, {frak('or')} `30` {frak('seconds.')}",
                reply_markup=markup([primary(frak("10s")), primary(frak("20s")), primary(frak("30s"))])
            )
            return

        set_media_delete_time(chat_id, seconds)
        await message.reply(
            f"✅ **{frak('Media Auto-Delete Timer Updated!')}**\n\n"
            f"⏱️ **{frak('New Time:')}** `{seconds}` {frak('seconds')}\n"
            f"🗑️ **{frak('Effect:')}** {frak('All media from non-certified members will be')}\n"
            f"   {frak('automatically deleted after')} `{seconds}` {frak('seconds.')}\n\n"
            f"_{frak('Certified members are exempt from this rule.')}_",
            reply_markup=markup([success(frak(f"Timer set to {seconds}s"))])
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

        media_time = get_media_delete_time(chat_id)
        title = get_group_title(chat_id) or frak("Not saved")
        photo = get_group_photo_id(chat_id)

        await message.reply(
            f"📊 **{frak('Group Protection Info')}**\n\n"
            f"💬 **{frak('Group:')}** `{message.chat.title}`\n"
            f"🆔 **{frak('Chat ID:')}** `{chat_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚙️ **{frak('Settings:')}**\n"
            f"• ⏱️ {frak('Media auto-delete:')} `{media_time}s`\n"
            f"• 📝 {frak('Protected title:')} `{title}`\n"
            f"• 🖼️ {frak('Protected photo:')} {'✅ Saved' if photo else '❌ Not saved'}\n"
            f"• ⭐ {frak('Certified members:')} `{certified_count}`\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ **{frak('Active Protections:')}**\n"
            f"• ✅ {frak('Slang/illegal word filter')}\n"
            f"• ✅ {frak('Media auto-delete for non-certified')}\n"
            f"• ✅ {frak('Group name protection')}\n"
            f"• ✅ {frak('Group photo protection')}\n"
            f"• ✅ {frak('Illegal media detection')}",
            reply_markup=markup(
                [primary(frak("Group Stats")), success(frak("All Systems Active ✅"))]
            )
        )
