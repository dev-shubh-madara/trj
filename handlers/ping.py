import time
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.font import frak
from utils.buttons import markup, primary, success, danger


def register(app: Client):

    @app.on_message(filters.command("ping"))
    async def cmd_ping(client: Client, message: Message):
        t1 = time.monotonic()
        msg = await message.reply(f"🏓 {frak('Pinging')}...")
        t2 = time.monotonic()
        latency_ms = round((t2 - t1) * 1000)

        if latency_ms < 200:
            status = frak("Excellent 🟢")
            kb = markup([success(frak(f"✦ {latency_ms}ms — Excellent ✦"))])
        elif latency_ms < 500:
            status = frak("Good 🟡")
            kb = markup([primary(frak(f"✦ {latency_ms}ms — Good ✦"))])
        else:
            status = frak("Slow 🔴")
            kb = markup([danger(frak(f"✦ {latency_ms}ms — Slow ✦"))])

        await msg.edit(
            f"🏓 **{frak('Pong!')}**\n\n"
            f"⚡ **{frak('Latency:')}** `{latency_ms}ms`\n"
            f"📶 **{frak('Status:')}** {status}\n\n"
            f"🤖 **{frak('Bot:')}** @GROUP_PROTECTER_GMS_bot\n"
            f"🛡️ **{frak('Server:')}** {frak('Online & Protecting')}\n\n"
            f"— **{frak('Powered by Madara')}** 🔥",
            reply_markup=kb
        )
