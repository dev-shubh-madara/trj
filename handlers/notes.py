import re
from pyrogram import Client, filters
from pyrogram.types import Message
from database import get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger


def _save_note(chat_id, name, content, creator_id):
    conn = get_conn()
    conn.execute(
        "INSERT INTO notes (chat_id, name, content, creator_id) VALUES (?,?,?,?) "
        "ON CONFLICT(chat_id, name) DO UPDATE SET content=excluded.content, creator_id=excluded.creator_id",
        (chat_id, name.lower(), content, creator_id)
    )
    conn.commit()


def _get_note(chat_id, name):
    conn = get_conn()
    row = conn.execute(
        "SELECT content FROM notes WHERE chat_id=? AND name=?", (chat_id, name.lower())
    ).fetchone()
    return row["content"] if row else None


def _del_note(chat_id, name):
    conn = get_conn()
    conn.execute("DELETE FROM notes WHERE chat_id=? AND name=?", (chat_id, name.lower()))
    conn.commit()


def _list_notes(chat_id):
    conn = get_conn()
    return [r["name"] for r in conn.execute(
        "SELECT name FROM notes WHERE chat_id=? ORDER BY name", (chat_id,)
    ).fetchall()]


def register(app: Client):

    @app.on_message(filters.command(["save", "note"]) & filters.group)
    async def cmd_save(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        parts = message.text.split(None, 2)
        if len(parts) < 3 and not message.reply_to_message:
            return await message.reply(
                f"**{frak('Usage:')}** `/save notename content`\n"
                f"_{frak('Or reply to a message with')} `/save notename`_",
                reply_markup=markup([primary(frak("✦ /save name text ✦"))])
            )
        name = parts[1].lower() if len(parts) >= 2 else None
        if not name:
            return await message.reply(f"**{frak('Provide a note name.')}**")

        if len(parts) >= 3:
            content = parts[2]
        elif message.reply_to_message:
            content = (message.reply_to_message.text or
                       message.reply_to_message.caption or "")
        else:
            return await message.reply(f"**{frak('Provide note content.')}**")

        _save_note(message.chat.id, name, content, uid)
        await message.reply(
            f"📝 **{frak('Note Saved!')}**\n\n"
            f"🔖 **{frak('Name:')}** `#{name}`\n"
            f"📋 **{frak('Content:')}** {content[:100]}{'...' if len(content)>100 else ''}\n\n"
            f"_{frak('Use')} `#{name}` {frak('to retrieve it.')}_",
            reply_markup=markup([success(frak(f"✦ #{name} Saved ✦"))])
        )

    @app.on_message(filters.command("get") & filters.group)
    async def cmd_get(client: Client, message: Message):
        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply(
                f"**{frak('Usage:')}** `/get notename`",
                reply_markup=markup([primary(frak("✦ /get notename ✦"))])
            )
        name = parts[1].lower()
        content = _get_note(message.chat.id, name)
        if not content:
            return await message.reply(
                f"**{frak('Note')}** `#{name}` **{frak('not found.')}**",
                reply_markup=markup([danger(frak("✦ Not Found ✦"))])
            )
        await message.reply(
            f"📝 **#{name}**\n\n{content}",
            reply_markup=markup([primary(frak(f"✦ #{name} ✦"))])
        )

    @app.on_message(filters.command("notes") & filters.group)
    async def cmd_notes(client: Client, message: Message):
        notes = _list_notes(message.chat.id)
        if not notes:
            return await message.reply(
                f"**{frak('No notes saved in this group.')}**\n"
                f"_{frak('Use /save name text to add notes.')}_",
                reply_markup=markup([primary(frak("✦ /save name text ✦"))])
            )
        lines = "\n".join(f"• `#{n}`" for n in notes)
        await message.reply(
            f"📋 **{frak('Saved Notes')}** ({len(notes)}):\n\n{lines}",
            reply_markup=markup([success(frak(f"✦ {len(notes)} Notes ✦"))])
        )

    @app.on_message(filters.command("clear") & filters.group)
    async def cmd_clear(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply(f"**{frak('Usage:')}** `/clear notename`")
        name = parts[1].lower()
        _del_note(message.chat.id, name)
        await message.reply(
            f"🗑️ **{frak('Note Deleted')}**\n`#{name}`",
            reply_markup=markup([danger(frak(f"✦ #{name} Deleted ✦"))])
        )

    @app.on_message(filters.command("clearall") & filters.group)
    async def cmd_clearall(client: Client, message: Message):
        from config import OWNER_ID
        from database import is_authorized
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        conn = get_conn()
        conn.execute("DELETE FROM notes WHERE chat_id=?", (message.chat.id,))
        conn.commit()
        await message.reply(
            f"🗑️ **{frak('All Notes Cleared')}**",
            reply_markup=markup([danger(frak("✦ All Notes Deleted ✦"))])
        )

    @app.on_message(filters.text & filters.group, group=3)
    async def hashtag_note(client: Client, message: Message):
        text = message.text or ""
        matches = re.findall(r'#(\w+)', text)
        if not matches:
            return
        for name in matches:
            content = _get_note(message.chat.id, name.lower())
            if content:
                await message.reply(
                    f"📝 **#{name}**\n\n{content}",
                    reply_markup=markup([primary(frak(f"✦ #{name} ✦"))])
                )
                break
