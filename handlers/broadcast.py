import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ParseMode

from config import OWNER_ID
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, em_row

PM = ParseMode.HTML
MADARA = f"\n\n— <b>{frak('Powered by Madara')}</b> 🔥"


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
                f"{em()} ⛔ <b>{frak('Owner Only Command')}</b>\n"
                f"<i>{frak('Only the bot owner can use broadcast.')}</i>"
                f"{MADARA}",
                parse_mode=PM,
                reply_markup=markup([danger(frak("✦ Owner Only ✦"))])
            )

        if not message.reply_to_message:
            chats = _get_all_chats()
            return await message.reply(
                f"{em_row(4)}\n\n"
                f"📢 <b>{frak('How to Broadcast')}</b>\n\n"
                f"{em()} 1. {frak('Write or forward any message to me')}\n"
                f"{em()} 2. {frak('Reply to it with')} <code>/broadcast</code>\n\n"
                f"{em()} 📡 <b>{frak('Known Groups:')}</b> <code>{len(chats)}</code>\n"
                f"<i>{frak('Supports text, photos, videos, documents.')}</i>"
                f"{MADARA}",
                parse_mode=PM,
                reply_markup=markup([primary(frak("✦ Reply to a message ✦"))])
            )

        chats = _get_all_chats()
        total = len(chats)

        if total == 0:
            return await message.reply(
                f"{em()} ⚠️ <b>{frak('No known groups yet.')}</b>\n\n"
                f"<i>{frak('The bot must receive at least one message in a group first.')}</i>"
                f"{MADARA}",
                parse_mode=PM,
                reply_markup=markup([danger(frak("✦ No Groups Found ✦"))])
            )

        status_msg = await message.reply(
            f"{em_row(3)}\n\n"
            f"📡 <b>{frak('Broadcasting...')}</b>\n\n"
            f"{em()} 📊 <b>{frak('Total Groups:')}</b> <code>{total}</code>\n"
            f"{em()} ✅ <b>{frak('Sent:')}</b> <code>0</code>  ❌ <b>{frak('Failed:')}</b> <code>0</code>",
            parse_mode=PM,
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
                        f"{em_row(3)}\n\n"
                        f"📡 <b>{frak('Broadcasting...')}</b>\n\n"
                        f"{em()} 📊 <b>{frak('Total:')}</b> <code>{total}</code>\n"
                        f"{em()} ✅ <b>{frak('Sent:')}</b> <code>{sent}</code>  "
                        f"❌ <b>{frak('Failed:')}</b> <code>{failed}</code>",
                        parse_mode=PM,
                        reply_markup=markup([primary(frak(f"✦ {i+1}/{total} ✦"))])
                    )
                except Exception:
                    pass
            await asyncio.sleep(0.05)

        await status_msg.edit(
            f"{em_row(5)}\n\n"
            f"✅ <b>{frak('Broadcast Complete!')}</b>\n\n"
            f"{em()} 📊 <b>{frak('Total:')}</b> <code>{total}</code>\n"
            f"{em()} ✅ <b>{frak('Sent:')}</b> <code>{sent}</code>\n"
            f"{em()} ❌ <b>{frak('Failed:')}</b> <code>{failed}</code>"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=markup(
                [success(frak(f"✦ {sent} Sent ✦")), danger(frak(f"✦ {failed} Failed ✦"))]
            )
        )

    @app.on_message(filters.command(["broadcast", "bcast"]) & filters.group)
    async def cmd_broadcast_group(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            return
        await message.reply(
            f"{em()} 📢 <b>{frak('Use Broadcast in PM')}</b>\n\n"
            f"<i>{frak('Open a private chat with me and reply to a message with')} /broadcast</i>"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=markup([primary(frak("✦ Use in Private Chat ✦"))])
        )
