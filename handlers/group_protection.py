import asyncio
import os
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import MessageServiceType
from database import (
    save_group_title, get_group_title,
    save_group_photo_id, get_group_photo_id,
    is_certified, is_authorized
)
from config import OWNER_ID
from utils.font import frak
from utils.buttons import markup, primary, success, danger


async def snapshot_group(client: Client, chat_id: int):
    try:
        chat = await client.get_chat(chat_id)
        if chat.title:
            save_group_title(chat_id, chat.title)
        if chat.photo and chat.photo.big_file_id:
            save_group_photo_id(chat_id, chat.photo.big_file_id)
    except Exception:
        pass


def register(app: Client):

    @app.on_message(filters.group & filters.service, group=0)
    async def handle_service(client: Client, message: Message):
        if not message.service:
            return

        chat_id = message.chat.id
        actor_id = message.from_user.id if message.from_user else None

        if actor_id and is_certified(actor_id, chat_id):
            if message.service == MessageServiceType.NEW_CHAT_TITLE:
                save_group_title(chat_id, message.new_chat_title)
            elif message.service == MessageServiceType.NEW_CHAT_PHOTO:
                try:
                    chat = await client.get_chat(chat_id)
                    if chat.photo and chat.photo.big_file_id:
                        save_group_photo_id(chat_id, chat.photo.big_file_id)
                except Exception:
                    pass
            return

        if message.service == MessageServiceType.NEW_CHAT_TITLE:
            new_title = message.new_chat_title
            old_title = get_group_title(chat_id)
            if old_title and new_title != old_title:
                try:
                    await asyncio.sleep(1)
                    await client.set_chat_title(chat_id, old_title)
                    actor_mention = message.from_user.mention if message.from_user else frak("Someone")
                    await client.send_message(
                        chat_id,
                        f"🔵 **{frak('Group Name Protected!')}**\n\n"
                        f"👤 **{frak('By:')}** {actor_mention}\n"
                        f"❌ **{frak('Attempted Name:')}** `{new_title}`\n"
                        f"✅ **{frak('Restored to:')}** `{old_title}`\n\n"
                        f"_{frak('Only certified members can change the group name.')}_",
                        reply_markup=markup([primary(frak("Group Name Restored ✅"))])
                    )
                except Exception:
                    pass
            elif not old_title:
                save_group_title(chat_id, new_title)

        elif message.service == MessageServiceType.NEW_CHAT_PHOTO:
            old_photo_id = get_group_photo_id(chat_id)
            actor_mention = message.from_user.mention if message.from_user else frak("Someone")
            if old_photo_id:
                try:
                    await asyncio.sleep(1)
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                        tmp_path = tmp.name
                    await client.download_media(old_photo_id, file_name=tmp_path)
                    await client.set_chat_photo(chat_id, photo=tmp_path)
                    os.unlink(tmp_path)
                    await client.send_message(
                        chat_id,
                        f"🔵 **{frak('Group Photo Protected!')}**\n\n"
                        f"👤 **{frak('By:')}** {actor_mention}\n"
                        f"✅ **{frak('Action:')}** {frak('Original photo restored')}\n\n"
                        f"_{frak('Only certified members can change the group photo.')}_",
                        reply_markup=markup([primary(frak("Group Photo Restored ✅"))])
                    )
                except Exception:
                    pass
            else:
                try:
                    chat = await client.get_chat(chat_id)
                    if chat.photo and chat.photo.big_file_id:
                        save_group_photo_id(chat_id, chat.photo.big_file_id)
                except Exception:
                    pass

        elif message.service == MessageServiceType.DELETE_CHAT_PHOTO:
            old_photo_id = get_group_photo_id(chat_id)
            actor_mention = message.from_user.mention if message.from_user else frak("Someone")
            if old_photo_id:
                try:
                    await asyncio.sleep(1)
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                        tmp_path = tmp.name
                    await client.download_media(old_photo_id, file_name=tmp_path)
                    await client.set_chat_photo(chat_id, photo=tmp_path)
                    os.unlink(tmp_path)
                    await client.send_message(
                        chat_id,
                        f"🔵 **{frak('Group Photo Deletion Blocked!')}**\n\n"
                        f"👤 **{frak('By:')}** {actor_mention}\n"
                        f"✅ **{frak('Action:')}** {frak('Original photo restored')}\n\n"
                        f"_{frak('Only certified members can remove the group photo.')}_",
                        reply_markup=markup([primary(frak("Group Photo Restored ✅"))])
                    )
                except Exception:
                    pass

    @app.on_message(filters.command("snapshotgroup") & filters.group)
    async def cmd_snapshot(client: Client, message: Message):
        user = message.from_user
        if user.id != OWNER_ID and not is_authorized(user.id):
            return

        chat_id = message.chat.id
        await snapshot_group(client, chat_id)
        title = get_group_title(chat_id) or frak("Not set")
        photo = get_group_photo_id(chat_id)

        await message.reply(
            f"📸 **{frak('Group Snapshot Saved')}**\n\n"
            f"📝 **{frak('Title:')}** `{title}`\n"
            f"🖼️ **{frak('Photo:')}** {'Saved ✅' if photo else 'Not set ❌'}\n\n"
            f"_{frak('The bot will now protect these settings.')}_",
            reply_markup=markup(
                [success(frak("Snapshot Saved ✅")), primary(frak("Now Protected 🛡️"))]
            )
        )
