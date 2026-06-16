import asyncio
import os
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import MessageServiceType, ChatMemberStatus, ParseMode
from database import (
    save_group_title, get_group_title,
    save_group_photo_id, get_group_photo_id,
    is_certified, is_authorized
)
from config import OWNER_ID
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, em_row

PM = ParseMode.HTML
MADARA = f"\n\n— <b>{frak('Powered by Madara')}</b> 🔥"


def _is_allowed(actor_id, chat_id):
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


async def _restore_photo(client, chat_id, old_photo_id, actor_mention):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        downloaded = await client.download_media(old_photo_id, file_name=tmp_path)
        if downloaded and os.path.exists(tmp_path):
            await client.set_chat_photo(chat_id, photo=tmp_path)
            await client.send_message(
                chat_id,
                f"{em_row(5)}\n\n"
                f"🔵 <b>{frak('Group Photo Protected!')}</b>\n\n"
                f"{em()} <b>{frak('By:')}</b> {actor_mention}\n"
                f"{em()} <b>{frak('Action:')}</b> {frak('Original photo restored')}\n\n"
                f"<i>{frak('Only the owner or certified members can change the group photo.')}</i>"
                f"{MADARA}",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Group Photo Restored ✅"))])
            )
    except Exception:
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
        me = await client.get_me()
        if not update.new_chat_member:
            return
        if update.new_chat_member.user.id != me.id:
            return
        if update.new_chat_member.status in (
            ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER
        ):
            await asyncio.sleep(2)
            await snapshot_group(client, update.chat.id)

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
                        f"{em_row(5)}\n\n"
                        f"🔵 <b>{frak('Group Name Protected!')}</b>\n\n"
                        f"{em()} <b>{frak('By:')}</b> {actor_mention}\n"
                        f"{em()} ❌ <b>{frak('Attempted:')}</b> <code>{new_title}</code>\n"
                        f"{em()} ✅ <b>{frak('Restored:')}</b> <code>{old_title}</code>\n\n"
                        f"<i>{frak('Only the owner or certified members can change the group name.')}</i>"
                        f"{MADARA}",
                        parse_mode=PM,
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
            f"{em_row(5)}\n\n"
            f"📸 <b>{frak('Group Snapshot Saved')}</b>\n\n"
            f"{em()} <b>{frak('Title:')}</b> <code>{title}</code>\n"
            f"{em()} <b>{frak('Photo:')}</b> {'Saved ✅' if photo else 'Not set ❌'}\n\n"
            f"<i>{frak('The bot will now protect these settings.')}</i>"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=markup(
                [success(frak("Snapshot Saved ✅")), primary(frak("Now Protected 🛡️"))]
            )
        )
