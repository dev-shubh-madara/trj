from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from database import add_authorized_user, remove_authorized_user, is_authorized
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default


def register(app: Client):

    @app.on_message(filters.command("auth") & filters.private)
    async def cmd_auth(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            await message.reply(
                f"⛔ **{frak('Access Denied')}**\n{frak('Only the bot owner can use this command.')}",
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        parts = message.text.split()
        if len(parts) < 2:
            await message.reply(
                f"❓ **{frak('Usage:')}** `/auth <telegram_user_id>`\n\n"
                f"{frak('Example:')} `/auth 123456789`",
                reply_markup=markup([primary(frak("Usage: /auth <user_id>"))])
            )
            return

        try:
            target_id = int(parts[1])
        except ValueError:
            await message.reply(
                f"❌ **{frak('Invalid ID')}**\n{frak('Please provide a valid numeric Telegram user ID.')}",
                reply_markup=markup([danger(frak("Invalid ID"))])
            )
            return

        add_authorized_user(target_id)
        await message.reply(
            f"✅ **{frak('User Authorized Successfully!')}**\n\n"
            f"👤 **{frak('User ID:')}** `{target_id}`\n"
            f"🔐 **{frak('Status:')}** {frak('Authorized to use the bot')}\n\n"
            f"_{frak('This user can now interact with the bot.')}_",
            reply_markup=markup([success(frak("Authorization Granted"))])
        )

    @app.on_message(filters.command("unauth") & filters.private)
    async def cmd_unauth(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            await message.reply(
                f"⛔ **{frak('Access Denied')}**",
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        parts = message.text.split()
        if len(parts) < 2:
            await message.reply(
                f"❓ **{frak('Usage:')}** `/unauth <telegram_user_id>`",
                reply_markup=markup([primary(frak("Usage: /unauth <user_id>"))])
            )
            return

        try:
            target_id = int(parts[1])
        except ValueError:
            await message.reply(
                f"❌ **{frak('Invalid ID.')}**",
                reply_markup=markup([danger(frak("Invalid ID"))])
            )
            return

        remove_authorized_user(target_id)
        await message.reply(
            f"🔴 **{frak('Authorization Revoked')}**\n\n"
            f"👤 **{frak('User ID:')}** `{target_id}`\n"
            f"🔐 **{frak('Status:')}** {frak('No longer authorized')}",
            reply_markup=markup([danger(frak("Authorization Revoked"))])
        )
