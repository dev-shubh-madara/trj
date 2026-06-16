import asyncio
import logging
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from database import init_db
from utils.emojis import load_emoji_packs, em, ems, em_row

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
import handlers.grouptools as grouptools_handler

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
    grouptools_handler.register(app)
    log.info("All 17 handlers registered.")


async def main():
    log.info("Initializing database...")
    init_db()
    log.info("Starting GuardBot v4...")
    app = create_app()
    register_all_handlers(app)

    async with app:
        me = await app.get_me()
        log.info(f"Bot: @{me.username} ({me.id}) | Owner: {OWNER_ID}")

        log.info("Loading premium emoji packs...")
        count = await load_emoji_packs(app)
        log.info(f"Emoji pool ready: {count} emojis")

        startup_text = (
            f"{em_row(6)}\n\n"
            f"{em()} <b>GuardBot v4 Online!</b> {em()}\n\n"
            f"@{me.username} | <code>{me.id}</code>\n\n"
            f"{em()} 17 handlers registered\n"
            f"{em()} {count} premium emojis loaded\n"
            f"{em()} HTML parse mode everywhere\n"
            f"{em()} /report → alerts all admins via PM\n"
            f"{em()} /ro /unro → read-only restriction\n"
            f"{em()} /afk /unafk → AFK auto-reply\n"
            f"{em()} /admins → list all admins\n"
            f"{em()} /info /id → user info lookup\n"
            f"{em()} /invite → generate invite link\n"
            f"{em()} /lock [all/media/sticker]\n\n"
            f"{em_row(6)}\n\n"
            f"— <b>Powered by Madara</b> 🔥"
        )
        try:
            await app.send_message(OWNER_ID, startup_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            log.warning(f"DM owner skipped ({e}) — send /start to the bot first.")

        log.info("GuardBot is protecting.")
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Stopped.")
    except Exception as e:
        log.exception(f"Fatal: {e}")
