import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from config import OWNER_ID
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default


async def _get_all_chats(client: Client):
    chats = []
    async for dialog in client.get_dialogs():
        if dialog.chat.type.value in ("group", "supergroup", "channel"):
            chats.append(dialog.chat.id)
    return chats


def register(app: Client):

    @app.on_message(filters.command("broadcast") & filters.private)
    async def cmd_broadcast(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            await message.reply(
                f"⛔ **{frak('Access Denied')}**\n{frak('Only the bot owner can broadcast.')}",
                reply_markup=markup([danger(frak("✦ Owner Only ✦"))])
            )
            return

        if not message.reply_to_message:
            await message.reply(
                f"📢 **{frak('Broadcast System')}**\n\n"
                f"{frak('Reply to a message and use')} `/broadcast` {frak('to send it to all groups.')}\n\n"
                f"**{frak('Supported')}:**\n"
                f"• {frak('Text messages')}\n"
                f"• {frak('Photos with captions')}\n"
                f"• {frak('Videos with captions')}\n"
                f"• {frak('Documents')}\n\n"
                f"_{frak('The message will be forwarded to all groups the bot is in.')}_",
                reply_markup=markup(
                    [primary(frak("✦ Reply to a message ✦"))]
                )
            )
            return

        status_msg = await message.reply(
            f"📡 **{frak('Broadcast Starting...')}**\n\n"
            f"⏳ {frak('Fetching all groups...')}",
            reply_markup=markup([primary(frak("✦ Broadcasting... ✦"))])
        )

        chats = await _get_all_chats(client)
        total = len(chats)
        sent = 0
        failed = 0
        broadcast_msg = message.reply_to_message

        await status_msg.edit(
            f"📡 **{frak('Broadcasting...')}**\n\n"
            f"📊 **{frak('Total Groups')}:** {total}\n"
            f"✅ **{frak('Sent')}:** 0\n"
            f"❌ **{frak('Failed')}:** 0",
            reply_markup=markup([primary(frak(f"✦ 0/{total} ✦"))])
        )

        for i, chat_id in enumerate(chats):
            try:
                await broadcast_msg.forward(chat_id)
                sent += 1
            except Exception:
                failed += 1

            if (i + 1) % 10 == 0:
                try:
                    await status_msg.edit(
                        f"📡 **{frak('Broadcasting...')}**\n\n"
                        f"📊 **{frak('Total')}:** {total}\n"
                        f"✅ **{frak('Sent')}:** {sent}\n"
                        f"❌ **{frak('Failed')}:** {failed}",
                        reply_markup=markup([primary(frak(f"✦ {i+1}/{total} ✦"))])
                    )
                except Exception:
                    pass

            await asyncio.sleep(0.05)

        await status_msg.edit(
            f"✅ **{frak('Broadcast Complete!')}**\n\n"
            f"📊 **{frak('Total Groups')}:** {total}\n"
            f"✅ **{frak('Successfully Sent')}:** {sent}\n"
            f"❌ **{frak('Failed')}:** {failed}\n\n"
            f"_{frak('Broadcast finished.')}_",
            reply_markup=markup(
                [success(frak(f"✦ Sent: {sent} ✦")), danger(frak(f"✦ Failed: {failed} ✦"))]
            )
        )

    @app.on_message(filters.command("bcast") & filters.group)
    async def cmd_bcast_group(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            return

        parts = message.text.split(None, 1)
        if len(parts) < 2 and not message.reply_to_message:
            await message.reply(
                f"📢 **{frak('Group Broadcast')}**\n\n"
                f"{frak('Reply to a message or write:')} `/bcast <message>`",
                reply_markup=markup([primary(frak("✦ Usage: /bcast text ✦"))])
            )
            return

        chats = await _get_all_chats(client)
        sent = 0
        failed = 0

        if message.reply_to_message:
            bcast = message.reply_to_message
            for chat_id in chats:
                try:
                    await bcast.forward(chat_id)
                    sent += 1
                    await asyncio.sleep(0.05)
                except Exception:
                    failed += 1
        else:
            text = parts[1]
            for chat_id in chats:
                try:
                    await client.send_message(chat_id, text)
                    sent += 1
                    await asyncio.sleep(0.05)
                except Exception:
                    failed += 1

        await message.reply(
            f"✅ **{frak('Broadcast Done')}**\n"
            f"✅ {frak('Sent')}: {sent} | ❌ {frak('Failed')}: {failed}",
            reply_markup=markup(
                [success(frak(f"✦ {sent} Sent ✦")), danger(frak(f"✦ {failed} Failed ✦"))]
            )
        )
