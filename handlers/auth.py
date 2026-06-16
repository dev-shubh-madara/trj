from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from config import OWNER_ID
from database import add_authorized_user, remove_authorized_user, is_authorized, get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default
from utils.emojis import em, em_row

PM = ParseMode.HTML


def register(app: Client):

    @app.on_message(filters.command("auth") & filters.private)
    async def cmd_auth(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            await message.reply(
                f"{em_row(3)}\n\n"
                f"⛔ <b>{frak('Access Denied')}</b>\n\n"
                f"{em()} {frak('Only the bot owner can use this command.')}",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        parts = message.text.split()
        if len(parts) < 2:
            await message.reply(
                f"{em_row(3)}\n\n"
                f"❓ <b>{frak('Usage:')}</b> <code>/auth &lt;user_id&gt;</code>\n\n"
                f"{em()} {frak('Example:')} <code>/auth 123456789</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Usage: /auth <user_id>"))])
            )
            return

        try:
            target_id = int(parts[1])
        except ValueError:
            await message.reply(
                f"{em()} <b>{frak('Invalid ID')}</b>\n"
                f"{frak('Please provide a valid numeric Telegram user ID.')}",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Invalid ID"))])
            )
            return

        add_authorized_user(target_id)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"✅ <b>{frak('User Authorized Successfully!')}</b>\n\n"
            f"{em()} <b>{frak('User ID:')}</b> <code>{target_id}</code>\n"
            f"{em()} <b>{frak('Status:')}</b> {frak('Authorized')}\n\n"
            f"<i>{frak('This user can now use admin commands in groups.')}</i>",
            parse_mode=PM,
            reply_markup=markup([success(frak("Authorization Granted"))])
        )

    @app.on_message(filters.command("unauth") & filters.private)
    async def cmd_unauth(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            await message.reply(
                f"{em()} ⛔ <b>{frak('Access Denied')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        parts = message.text.split()
        if len(parts) < 2:
            await message.reply(
                f"{em()} <b>{frak('Usage:')}</b> <code>/unauth &lt;user_id&gt;</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Usage: /unauth <user_id>"))])
            )
            return

        try:
            target_id = int(parts[1])
        except ValueError:
            await message.reply(
                f"{em()} <b>{frak('Invalid ID.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Invalid ID"))])
            )
            return

        remove_authorized_user(target_id)
        await message.reply(
            f"{em_row(3)}\n\n"
            f"🔴 <b>{frak('Authorization Revoked')}</b>\n\n"
            f"{em()} <b>{frak('User ID:')}</b> <code>{target_id}</code>\n"
            f"{em()} <b>{frak('Status:')}</b> {frak('No longer authorized')}",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Authorization Revoked"))])
        )

    @app.on_message(filters.command("authlist") & filters.private)
    async def cmd_authlist(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            return
        conn = get_conn()
        rows = conn.execute("SELECT user_id FROM authorized_users").fetchall()
        if not rows:
            return await message.reply(
                f"{em()} <b>{frak('No authorized users yet.')}</b>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Use /auth <id> to add"))])
            )
        lines = "\n".join(f"{em()} <code>{r['user_id']}</code>" for r in rows)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"🔐 <b>{frak('Authorized Users')}</b> ({len(rows)}):\n\n"
            f"{lines}",
            parse_mode=PM,
            reply_markup=markup([success(frak(f"{len(rows)} Authorized Users"))])
        )
