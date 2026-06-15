import asyncio
import os
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import MessageServiceType, ChatMemberStatus
from database import (
    save_group_title, get_group_title,
    save_group_photo_id, get_group_photo_id,
    is_certified, is_authorized
)
from config import OWNER_ID
from utils.font import frak
from utils.buttons import markup, primary, success, danger


def _is_allowed(actor_id, chat_id):
    """Owner or certified member — allowed to change group settings."""
    if actor_id is None:
        return False
    if actor_id == OWNER_ID:
        return True
    if is_certified(actor_id, chat_id):
        return True
    return False


async def snapshot_group(client: Client, chat_id: int):
    try:
        chat = await client.get_chat(chat_id)
        if chat.title:
            save_group_title(chat_id, chat.title)
        if chat.photo and chat.photo.big_file_id:
            save_group_photo_id(chat_id, chat.photo.big_file_id)
    except Exception:
        pass


async def _restore_photo(client: Client, chat_id: int, old_photo_id: str, actor_mention: str):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        downloaded = await client.download_media(old_photo_id, file_name=tmp_path)
        if downloaded and os.path.exists(tmp_path):
            await client.set_chat_photo(chat_id, photo=tmp_path)
            await client.send_message(
                chat_id,
                f"🔵 **{frak('Group Photo Protected!')}**\n\n"
                f"👤 **{frak('By:')}** {actor_mention}\n"
                f"✅ **{frak('Action:')}** {frak('Original photo restored')}\n\n"
                f"_{frak('Only the owner or certified members can change the group photo.')}_\n\n"
                f"— **{frak('Powered by Madara')}** 🔥",
                reply_markup=markup([primary(frak("Group Photo Restored ✅"))])
            )
    except Exception as e:
        pass
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def register(app: Client):

    @app.on_chat_member_updated()
    async def on_bot_added(client: Client, update: ChatMemberUpdated):
        """Auto-snapshot when bot is added to a group."""
        me = await client.get_me()
        if not update.new_chat_member:
            return
        if update.new_chat_member.user.id != me.id:
            return
        if update.new_chat_member.status in (
            ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER
        ):
            chat_id = update.chat.id
            await asyncio.sleep(2)
            await snapshot_group(client, chat_id)

    @app.on_message(filters.group & filters.service, group=0)
    async def handle_service(client: Client, message: Message):
        if not message.service:
            return

        chat_id = message.chat.id
        actor_id = message.from_user.id if message.from_user else None
        actor_mention = message.from_user.mention if message.from_user else frak("Someone")

        allowed = _is_allowed(actor_id, chat_id)

        if message.service == MessageServiceType.NEW_CHAT_TITLE:
            new_title = message.new_chat_title
            if allowed:
                save_group_title(chat_id, new_title)
                return

            old_title = get_group_title(chat_id)
            if old_title and new_title != old_title:
                try:
                    await asyncio.sleep(1)
                    await client.set_chat_title(chat_id, old_title)
                    await client.send_message(
                        chat_id,
                        f"🔵 **{frak('Group Name Protected!')}**\n\n"
                        f"👤 **{frak('By:')}** {actor_mention}\n"
                        f"❌ **{frak('Attempted Name:')}** `{new_title}`\n"
                        f"✅ **{frak('Restored to:')}** `{old_title}`\n\n"
                        f"_{frak('Only the owner or certified members can change the group name.')}_\n\n"
                        f"— **{frak('Powered by Madara')}** 🔥",
                        reply_markup=markup([primary(frak("Group Name Restored ✅"))])
                    )
                except Exception:
                    pass
            elif not old_title:
                save_group_title(chat_id, new_title)

        elif message.service == MessageServiceType.NEW_CHAT_PHOTO:
            if allowed:
                try:
                    chat = await client.get_chat(chat_id)
                    if chat.photo and chat.photo.big_file_id:
                        save_group_photo_id(chat_id, chat.photo.big_file_id)
                except Exception:
                    pass
                return

            old_photo_id = get_group_photo_id(chat_id)
            if old_photo_id:
                await asyncio.sleep(1)
                await _restore_photo(client, chat_id, old_photo_id, actor_mention)
            else:
                try:
                    chat = await client.get_chat(chat_id)
                    if chat.photo and chat.photo.big_file_id:
                        save_group_photo_id(chat_id, chat.photo.big_file_id)
                except Exception:
                    pass

        elif message.service == MessageServiceType.DELETE_CHAT_PHOTO:
            if allowed:
                return

            old_photo_id = get_group_photo_id(chat_id)
            if old_photo_id:
                await asyncio.sleep(1)
                await _restore_photo(client, chat_id, old_photo_id, actor_mention)

    @app.on_message(filters.command("snapshotgroup") & filters.group)
    async def cmd_snapshot(client: Client, message: Message):
        user = message.from_user
        if user.id != OWNER_ID and not is_authorized(user.id):
            return

        chat_id = message.chat.id
        await snapshot_group(client, chat_id)
        title = get_group_title(chat_id) or "Not set"
        photo = get_group_photo_id(chat_id)

        await message.reply(
            f"📸 **{frak('Group Snapshot Saved')}**\n\n"
            f"📝 **{frak('Title:')}** `{title}`\n"
            f"🖼️ **{frak('Photo:')}** {'Saved ✅' if photo else 'Not set ❌'}\n\n"
            f"_{frak('The bot will now protect these settings.')}_\n\n"
            f"— **{frak('Powered by Madara')}** 🔥",
            reply_markup=markup(
                [success(frak("Snapshot Saved ✅")), primary(frak("Now Protected 🛡️"))]
            )
        )
