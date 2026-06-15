import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from config import OWNER_ID
from database import is_authorized
from utils.font import frak
from utils.buttons import markup, primary, success, danger


def register(app: Client):

    @app.on_message(filters.command("clgroup") & filters.group)
    async def cmd_clgroup(client: Client, message: Message):
        user = message.from_user
        if user.id != OWNER_ID and not is_authorized(user.id):
            await message.reply(
                f"⛔ **{frak('Not Authorized')}**",
                reply_markup=markup([danger(frak("✦ Unauthorized ✦"))])
            )
            return

        try:
            chat_member = await client.get_chat_member(message.chat.id, user.id)
            if chat_member.status.value not in ("owner", "administrator"):
                await message.reply(
                    f"⛔ **{frak('Admins only.')}**",
                    reply_markup=markup([danger(frak("✦ Admins Only ✦"))])
                )
                return
        except Exception:
            return

        notice = await message.reply(
            f"🗑️ **{frak('Clearing Group...')}**\n\n"
            f"⚡ _{frak('Deleting all messages at max speed...')}_\n"
            f"⏳ {frak('Please wait...')}",
            reply_markup=markup([danger(frak("✦ Clearing... ✦"))])
        )

        deleted_total = 0
        batch_size = 100

        try:
            message_ids = []
            async for msg in client.get_chat_history(message.chat.id, limit=3000):
                if msg.id != notice.id:
                    message_ids.append(msg.id)

            for i in range(0, len(message_ids), batch_size):
                chunk = message_ids[i:i + batch_size]
                try:
                    await client.delete_messages(message.chat.id, chunk)
                    deleted_total += len(chunk)
                except Exception:
                    for mid in chunk:
                        try:
                            await client.delete_messages(message.chat.id, [mid])
                            deleted_total += 1
                        except Exception:
                            pass

            try:
                await notice.edit(
                    f"✅ **{frak('Group Cleared!')}**\n\n"
                    f"🗑️ **{frak('Deleted')}:** {deleted_total} {frak('messages')}\n"
                    f"⚡ **{frak('Speed')}:** {frak('Max batch speed')}\n"
                    f"👮 **{frak('By')}:** {user.mention}",
                    reply_markup=markup(
                        [success(frak(f"✦ {deleted_total} Msgs Deleted ✦")),
                         primary(frak("✦ Group Cleared ✦"))]
                    )
                )
            except Exception:
                pass

        except Exception as e:
            try:
                await notice.edit(
                    f"❌ **{frak('Error clearing group')}**\n\n`{str(e)}`",
                    reply_markup=markup([danger(frak("✦ Error ✦"))])
                )
            except Exception:
                pass
