import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from config import OWNER_ID
from database import is_authorized
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default

STICKER_SET = "guri20_by_fStikBot"
_sticker_cache = []

MADARA = f"\n\n— **{frak('Powered by Madara')}** 🔥"

HELP_TEXT = f"""
🤖 **{frak('GuardBot Command Center')}**{MADARA}

━━━━━━━━━━━━━━━━━━━━

🔐 **{frak('Owner')}** _(Private)_
`/auth <id>` · `/unauth <id>` · `/broadcast`

━━━━━━━━━━━━━━━━━━━━

⭐ **{frak('Certification')}**
`/giveaura` · `/removeaura` · `/certified`
`/snapshotgroup` · `/approve` · `/unapprove`

━━━━━━━━━━━━━━━━━━━━

👋 **{frak('Welcome')}**
`/setwelcome <text>` · `/setwelcome off` · `/welcome`
_{frak('Variables:')}_ `{{name}}` `{{first}}` `{{chat}}` `{{id}}`

━━━━━━━━━━━━━━━━━━━━

📝 **{frak('Notes')}** _(like MissRose)_
`/save name text` · `/get name` · `/notes`
`/clear name` · `/clearall` · `#notename`

━━━━━━━━━━━━━━━━━━━━

📜 **{frak('Rules')}**
`/setrules <text>` · `/rules` · `/resetrules`

━━━━━━━━━━━━━━━━━━━━

🔍 **{frak('Filters')}** _(Auto-replies)_
`/filter keyword reply` · `/filters`
`/stop keyword` · `/stopall`

━━━━━━━━━━━━━━━━━━━━

🌊 **{frak('Anti-Flood')}**
`/setflood N` · `/flood` · `/setflood 0` _{frak('disable')}_

━━━━━━━━━━━━━━━━━━━━

🔨 **{frak('Ban & Kick')}**
`/ban` · `/unban` · `/tban` · `/kick`

━━━━━━━━━━━━━━━━━━━━

🔇 **{frak('Mute')}**
`/mute` · `/unmute` · `/tmute`

━━━━━━━━━━━━━━━━━━━━

⚠️ **{frak('Warns')}** _(3 = auto ban)_
`/warn` · `/unwarn` · `/warns` · `/resetwarns`

━━━━━━━━━━━━━━━━━━━━

📌 **{frak('Messages')}**
`/pin` · `/unpin` · `/unpinall`
`/del` · `/purge` · `/clgroup`

━━━━━━━━━━━━━━━━━━━━

👮 **{frak('Admin')}**
`/promote` · `/demote` · `/title` · `/admins`

━━━━━━━━━━━━━━━━━━━━

🔒 **{frak('Group')}**
`/lock` · `/unlock` · `/setgrouppic <10|20|30>`
`/groupinfo` · `/info` · `/id` · `/help`
""".strip()


async def _get_random_sticker(client: Client):
    global _sticker_cache
    if not _sticker_cache:
        try:
            ss = await client.get_sticker_set(STICKER_SET)
            _sticker_cache = [s.file_id for s in ss.stickers]
        except Exception:
            return None
    return random.choice(_sticker_cache) if _sticker_cache else None


async def _send_start_animation(client: Client, chat_id: int, user_name: str, is_owner: bool, is_auth: bool):
    me = await client.get_me()
    role_val = frak("Owner 👑") if is_owner else frak("Authorized User ✅")

    sticker_id = await _get_random_sticker(client)
    sticker_msg = None
    if sticker_id:
        try:
            sticker_msg = await client.send_sticker(chat_id, sticker_id)
        except Exception:
            pass

    await asyncio.sleep(0.8)

    anim = await client.send_message(
        chat_id,
        f"**{frak('HLO THERE')}** . . . . ."
    )
    await asyncio.sleep(1.0)

    await anim.edit(
        f"**{frak('HLO THERE')}** . . . . .\n\n"
        f"⚡ **{frak('STARTING AURA PROTECTOR')}** . . ."
    )
    await asyncio.sleep(1.2)

    await anim.edit(
        f"**{frak('HLO THERE')}** . . . . .\n\n"
        f"⚡ **{frak('STARTING AURA PROTECTOR')}** . . .\n\n"
        f"🛡️ **{frak('LOADING SYSTEMS')}** . . . ✅"
    )
    await asyncio.sleep(1.0)

    try:
        await anim.delete()
    except Exception:
        pass

    main_msg = await client.send_message(
        chat_id,
        f"🤖 **{frak('GuardBot — Group Shield')}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 {frak('Welcome back')}, **{user_name}**!\n"
        f"🎖️ {frak('Role')}: {role_val}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🛡️ **{frak('I am your Group Guardian')}**\n"
        f"_{frak('Protecting your group from hateful content,')}_\n"
        f"_{frak('slang, illegal media, and unauthorized changes.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ _{frak('Add me to your group and make me Admin!')}_"
        f"{MADARA}",
        reply_markup=markup(
            [
                primary(frak("✦ Help & Commands ✦"), data="show_help"),
                success(frak("✦ Add to Group ✦"),
                        url=f"https://t.me/{me.username}?startgroup=true")
            ],
            [
                primary(frak("✦ Group Info ✦"), data="show_info"),
                danger(frak("✦ Broadcast ✦"), data="show_broadcast")
            ]
        )
    )
    return main_msg


def register(app: Client):

    @app.on_message(filters.command("start") & filters.private)
    async def cmd_start(client: Client, message: Message):
        uid = message.from_user.id
        is_owner = uid == OWNER_ID
        is_auth = is_authorized(uid)

        if not is_owner and not is_auth:
            await message.reply(
                f"🔒 **{frak('Access Restricted')}**\n\n"
                f"{frak('You are not authorized to use this bot.')}\n"
                f"{frak('Contact the owner to get access.')}\n\n"
                f"**{frak('Owner Command:')}** `/auth {uid}`"
                f"{MADARA}",
                reply_markup=markup([danger(frak("✦ Unauthorized ✦"))])
            )
            return

        name = message.from_user.first_name or "User"
        await _send_start_animation(
            client, message.chat.id, name, is_owner, is_auth
        )

    @app.on_callback_query(filters.regex("^show_help$"))
    async def cb_help(client: Client, query: CallbackQuery):
        await query.answer()
        me = await client.get_me()
        await query.message.edit(
            HELP_TEXT,
            reply_markup=markup(
                [
                    success(frak("✦ Back to Menu ✦"), data="show_start"),
                    primary(frak("✦ Add to Group ✦"),
                            url=f"https://t.me/{me.username}?startgroup=true")
                ]
            )
        )

    @app.on_callback_query(filters.regex("^show_start$"))
    async def cb_back_start(client: Client, query: CallbackQuery):
        await query.answer()
        uid = query.from_user.id
        is_owner = uid == OWNER_ID
        is_auth = is_authorized(uid)
        me = await client.get_me()
        name = query.from_user.first_name or "User"
        role_val = frak("Owner 👑") if is_owner else frak("Authorized User ✅")
        await query.message.edit(
            f"🤖 **{frak('GuardBot — Group Shield')}**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👋 {frak('Welcome back')}, **{name}**!\n"
            f"🎖️ {frak('Role')}: {role_val}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ **{frak('I am your Group Guardian')}**\n"
            f"_{frak('Protecting your group from hateful content,')}_\n"
            f"_{frak('slang, illegal media, and unauthorized changes.')}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ _{frak('Add me to your group and make me Admin!')}_"
            f"{MADARA}",
            reply_markup=markup(
                [
                    primary(frak("✦ Help & Commands ✦"), data="show_help"),
                    success(frak("✦ Add to Group ✦"),
                            url=f"https://t.me/{me.username}?startgroup=true")
                ],
                [
                    primary(frak("✦ Group Info ✦"), data="show_info"),
                    danger(frak("✦ Broadcast ✦"), data="show_broadcast")
                ]
            )
        )

    @app.on_callback_query(filters.regex("^show_info$"))
    async def cb_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.edit(
            f"ℹ️ **{frak('About GuardBot')}**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🤖 **{frak('Version:')}** 4.0\n"
            f"⚙️ **{frak('Framework:')}** Kurigram v2.2.23\n"
            f"🐍 **{frak('Language:')}** Python 3.11\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ **{frak('Active Protections:')}**\n"
            f"• ✅ {frak('Slang filter — all languages + bots')}\n"
            f"• ✅ {frak('Illegal media auto-removal')}\n"
            f"• ✅ {frak('Media auto-delete timer')}\n"
            f"• ✅ {frak('Group name & photo shield')}\n"
            f"• ✅ {frak('Certified member system')}\n"
            f"• ✅ {frak('Full admin suite (like MissRose)')}\n"
            f"• ✅ {frak('Notes, Rules, Filters system')}\n"
            f"• ✅ {frak('Anti-Flood protection')}\n"
            f"• ✅ {frak('Welcome messages with photo')}\n"
            f"• ✅ {frak('Owner broadcast system')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            reply_markup=markup(
                [
                    success(frak("✦ Back to Menu ✦"), data="show_start"),
                    primary(frak("✦ Commands ✦"), data="show_help")
                ]
            )
        )

    @app.on_callback_query(filters.regex("^show_broadcast$"))
    async def cb_broadcast(client: Client, query: CallbackQuery):
        await query.answer()
        if query.from_user.id != OWNER_ID:
            await query.answer(frak("Owner only!"), show_alert=True)
            return
        await query.message.edit(
            f"📢 **{frak('Broadcast System')}**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1. {frak('Write or forward a message to me in PM')}\n"
            f"2. {frak('Reply to it with')} `/broadcast`\n\n"
            f"📡 {frak('Sent to all groups the bot is in.')}"
            f"{MADARA}",
            reply_markup=markup(
                [
                    primary(frak("✦ Back to Menu ✦"), data="show_start"),
                    success(frak("✦ Go to PM ✦"), data="noop")
                ]
            )
        )

    @app.on_message(filters.command("help"))
    async def cmd_help(client: Client, message: Message):
        me = await client.get_me()
        await message.reply(
            HELP_TEXT,
            reply_markup=markup(
                [
                    primary(frak("✦ Add to Group ✦"),
                            url=f"https://t.me/{me.username}?startgroup=true"),
                    success(frak("✦ Back to Menu ✦"), data="show_start")
                ]
            )
        )

    @app.on_callback_query(filters.regex("^noop$"))
    async def cb_noop(client: Client, query: CallbackQuery):
        await query.answer()
