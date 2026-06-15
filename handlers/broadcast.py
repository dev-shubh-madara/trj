import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from config import OWNER_ID
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger

MADARA = f"\n\n— **{frak('Powered by Madara')}** 🔥"


def _save_chat(chat_id: int, title: str, chat_type: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO known_chats (chat_id, title, chat_type) VALUES (?,?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title",
        (chat_id, title or "", chat_type)
    )
    conn.commit()


def _get_all_chats():
    conn = get_conn()
    return [r["chat_id"] for r in conn.execute(
        "SELECT chat_id FROM known_chats WHERE chat_type IN ('group','supergroup')"
    ).fetchall()]


def register(app: Client):

    @app.on_message(filters.group, group=99)
    async def track_chat(client: Client, message: Message):
        """Silently record every group the bot receives messages in."""
        try:
            ct = message.chat.type.value
            if ct in ("group", "supergroup"):
                _save_chat(message.chat.id, message.chat.title or "", ct)
        except Exception:
            pass

    @app.on_message(filters.command(["broadcast", "bcast"]) & filters.private)
    async def cmd_broadcast_private(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply(
                f"⛔ **{frak('Owner Only Command')}**\n"
                f"_{frak('Only the bot owner can use broadcast.')}_"
                f"{MADARA}",
                reply_markup=markup([danger(frak("✦ Owner Only ✦"))])
            )

        if not message.reply_to_message:
            chats = _get_all_chats()
            return await message.reply(
                f"📢 **{frak('How to Broadcast')}**\n\n"
                f"1. {frak('Write or forward any message to me')}\n"
                f"2. {frak('Reply to it with')} `/broadcast`\n\n"
                f"📡 **{frak('Known Groups:')}** {len(chats)}\n"
                f"_{frak('Supports text, photos, videos, documents.')}_"
                f"{MADARA}",
                reply_markup=markup([primary(frak("✦ Reply to a message ✦"))])
            )

        chats = _get_all_chats()
        total = len(chats)

        if total == 0:
            return await message.reply(
                f"⚠️ **{frak('No known groups yet.')}**\n\n"
                f"_{frak('The bot needs to receive at least one message in a group before it can broadcast there.')}_"
                f"{MADARA}",
                reply_markup=markup([danger(frak("✦ No Groups Found ✦"))])
            )

        status_msg = await message.reply(
            f"📡 **{frak('Broadcasting...')}**\n\n"
            f"📊 **{frak('Total Groups:')}** {total}\n"
            f"✅ **{frak('Sent:')}** 0  ❌ **{frak('Failed:')}** 0",
            reply_markup=markup([primary(frak(f"✦ 0/{total} ✦"))])
        )

        sent = failed = 0
        bcast = message.reply_to_message

        for i, chat_id in enumerate(chats):
            try:
                await bcast.forward(chat_id)
                sent += 1
            except Exception:
                failed += 1

            if (i + 1) % 10 == 0 or i == total - 1:
                try:
                    await status_msg.edit(
                        f"📡 **{frak('Broadcasting...')}**\n\n"
                        f"📊 **{frak('Total:')}** {total}\n"
                        f"✅ **{frak('Sent:')}** {sent}  ❌ **{frak('Failed:')}** {failed}",
                        reply_markup=markup([primary(frak(f"✦ {i+1}/{total} ✦"))])
                    )
                except Exception:
                    pass
            await asyncio.sleep(0.05)

        await status_msg.edit(
            f"✅ **{frak('Broadcast Complete!')}**\n\n"
            f"📊 **{frak('Total:')}** {total}\n"
            f"✅ **{frak('Sent:')}** {sent}  ❌ **{frak('Failed:')}** {failed}"
            f"{MADARA}",
            reply_markup=markup(
                [success(frak(f"✦ {sent} Sent ✦")), danger(frak(f"✦ {failed} Failed ✦"))]
            )
        )

    @app.on_message(filters.command(["broadcast", "bcast"]) & filters.group)
    async def cmd_broadcast_group(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            return
        await message.reply(
            f"📢 **{frak('Use Broadcast in PM')}**\n\n"
            f"_{frak('Open a private chat with me and reply to a message with')} `/broadcast`_"
            f"{MADARA}",
            reply_markup=markup([primary(frak("✦ Use in Private Chat ✦"))])
        )
