import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, ems, em_row

PM = ParseMode.HTML


def register(app: Client):

    @app.on_message(filters.command("ping"))
    async def cmd_ping(client: Client, message: Message):
        t1 = time.monotonic()
        msg = await message.reply(
            f"{em()} <b>{frak('Pinging')}...</b>",
            parse_mode=PM
        )
        t2 = time.monotonic()
        ms = round((t2 - t1) * 1000)

        if ms < 200:
            status = frak("Excellent 🟢")
            kb = markup([success(frak(f"✦ {ms}ms — Excellent ✦"))])
        elif ms < 500:
            status = frak("Good 🟡")
            kb = markup([primary(frak(f"✦ {ms}ms — Good ✦"))])
        else:
            status = frak("Slow 🔴")
            kb = markup([danger(frak(f"✦ {ms}ms — Slow ✦"))])

        await msg.edit(
            f"{em_row(5)}\n\n"
            f"🏓 <b>{frak('Pong!')}</b>\n\n"
            f"{em()} <b>{frak('Latency:')}</b> <code>{ms}ms</code>\n"
            f"{em()} <b>{frak('Status:')}</b> {status}\n"
            f"{em()} <b>{frak('Bot:')}</b> @GROUP_PROTECTER_GMS_bot\n"
            f"{em()} <b>{frak('Server:')}</b> {frak('Online & Protecting')}\n\n"
            f"{em_row(5)}\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=kb
        )
