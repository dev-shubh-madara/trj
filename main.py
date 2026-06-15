import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from database import init_db

import handlers.help as help_handler
import handlers.auth as auth_handler
import handlers.certified as certified_handler
import handlers.media_filter as media_handler
import handlers.word_filter as word_handler
import handlers.group_protection as group_protection_handler
import handlers.settings as settings_handler
import handlers.admin as admin_handler
import handlers.welcome as welcome_handler
import handlers.broadcast as broadcast_handler
import handlers.clgroup as clgroup_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("GuardBot")


def create_app() -> Client:
    return Client(
        "guardbot_session",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )


def register_all_handlers(app: Client):
    help_handler.register(app)
    auth_handler.register(app)
    certified_handler.register(app)
    group_protection_handler.register(app)
    word_handler.register(app)
    media_handler.register(app)
    settings_handler.register(app)
    admin_handler.register(app)
    welcome_handler.register(app)
    broadcast_handler.register(app)
    clgroup_handler.register(app)
    log.info("All handlers registered successfully.")


async def main():
    log.info("Initializing database...")
    init_db()

    log.info("Starting GuardBot...")
    app = create_app()
    register_all_handlers(app)

    async with app:
        me = await app.get_me()
        log.info(f"Bot started: @{me.username} (ID: {me.id})")
        log.info(f"Owner ID: {OWNER_ID}")
        log.info("GuardBot is now running and protecting groups!")

        try:
            await app.send_message(
                OWNER_ID,
                f"🤖 **GuardBot is Online!**\n\n"
                f"✅ Bot: @{me.username}\n"
                f"🆔 Bot ID: `{me.id}`\n"
                f"👑 Owner: `{OWNER_ID}`\n\n"
                f"🆕 **New Features Active:**\n"
                f"• 👋 Welcome messages with profile photo\n"
                f"• 📢 Broadcast system (`/broadcast`)\n"
                f"• 🗑️ Group clear command (`/clgroup`)\n"
                f"• 🤖 Bot illegal message filter\n\n"
                f"Send /start to see the full command menu."
            )
        except Exception:
            pass

        log.info("Bot is idle. Press Ctrl+C to stop.")
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("GuardBot stopped by user.")
    except Exception as e:
        log.exception(f"Fatal error: {e}")
