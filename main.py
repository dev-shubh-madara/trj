import asyncio
import logging
from pyrogram import Client

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
import handlers.notes as notes_handler
import handlers.rules as rules_handler
import handlers.filters_handler as filters_handler
import handlers.antiflood as antiflood_handler
import handlers.ping as ping_handler

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
    notes_handler.register(app)
    rules_handler.register(app)
    filters_handler.register(app)
    antiflood_handler.register(app)
    ping_handler.register(app)
    log.info("All 16 handlers registered.")


async def main():
    log.info("Initializing database...")
    init_db()
    log.info("Starting GuardBot v4...")
    app = create_app()
    register_all_handlers(app)

    async with app:
        me = await app.get_me()
        log.info(f"Bot: @{me.username} ({me.id}) | Owner: {OWNER_ID}")
        try:
            await app.send_message(
                OWNER_ID,
                f"🤖 **GuardBot v4 Online!**\n\n"
                f"@{me.username} | `{me.id}`\n\n"
                f"✅ Colorful command button menu\n"
                f"✅ Broadcast = owner only\n"
                f"✅ Welcome fixed (groups + supergroups)\n"
                f"✅ Profile photo as spoiler in welcome\n"
                f"✅ /ping command added\n"
                f"✅ Notes · Rules · Filters · Anti-Flood\n"
                f"✅ Powered by Madara 🔥"
            )
        except Exception:
            pass
        log.info("GuardBot is protecting.")
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Stopped.")
    except Exception as e:
        log.exception(f"Fatal: {e}")
