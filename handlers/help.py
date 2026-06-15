from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ButtonStyle

from config import OWNER_ID
from database import is_authorized
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default


HELP_TEXT = f"""
🤖 **{frak('GuardBot — Command Center')}**

━━━━━━━━━━━━━━━━━━━━

🔐 **{frak('Owner Commands')}** _(Private Chat)_
• `/auth <id>` — {frak('Authorize a user to use the bot')}
• `/unauth <id>` — {frak('Remove user authorization')}
• `/start` — {frak('Show welcome screen')}

━━━━━━━━━━━━━━━━━━━━

⭐ **{frak('Certification System')}** _(Group)_
• `/giveaura` — {frak('Reply to certify a member (makes admin)')}
• `/removeaura` — {frak('Revoke certification')}
• `/certified` — {frak('List all certified members')}
• `/snapshotgroup` — {frak('Save group name & photo to protect')}

━━━━━━━━━━━━━━━━━━━━

🔨 **{frak('Ban & Kick')}** _(Group / Admin)_
• `/ban [@user] [reason]` — {frak('Permanently ban a user')}
• `/unban [@user]` — {frak('Unban a user')}
• `/tban [@user] [time] [reason]` — {frak('Temporarily ban (1h, 2d)')}
• `/kick [@user] [reason]` — {frak('Kick user (can rejoin)')}

━━━━━━━━━━━━━━━━━━━━

🔇 **{frak('Mute System')}** _(Group / Admin)_
• `/mute [@user] [reason]` — {frak('Mute a user')}
• `/unmute [@user]` — {frak('Unmute a user')}
• `/tmute [@user] [time]` — {frak('Temporarily mute (10m, 1h, 1d)')}

━━━━━━━━━━━━━━━━━━━━

⚠️ **{frak('Warning System')}** _(Group / Admin)_
• `/warn [@user] [reason]` — {frak('Warn a user (3 warns = ban)')}
• `/unwarn [@user]` — {frak('Remove last warning')}
• `/warns [@user]` — {frak('Check warnings count')}
• `/resetwarns [@user]` — {frak('Reset all warnings')}

━━━━━━━━━━━━━━━━━━━━

📌 **{frak('Message Management')}** _(Group / Admin)_
• `/pin` — {frak('Pin replied message')}
• `/unpin` — {frak('Unpin a message')}
• `/unpinall` — {frak('Unpin all messages')}
• `/del` — {frak('Delete replied message')}
• `/purge` — {frak('Delete messages from reply to now')}

━━━━━━━━━━━━━━━━━━━━

👮 **{frak('Admin Management')}** _(Group / Admin)_
• `/promote [@user]` — {frak('Promote to admin')}
• `/demote [@user]` — {frak('Demote from admin')}
• `/title [@user] [text]` — {frak('Set admin title')}
• `/admins` — {frak('List all group admins')}

━━━━━━━━━━━━━━━━━━━━

🔒 **{frak('Group Lock')}** _(Group / Admin)_
• `/lock` — {frak('Lock group (no one can send)')}
• `/unlock` — {frak('Unlock group')}

━━━━━━━━━━━━━━━━━━━━

⚙️ **{frak('Settings & Info')}** _(Group)_
• `/setgrouppic <10|20|30>` — {frak('Set media auto-delete timer')}
• `/groupinfo` — {frak('Show current protection settings')}
• `/info [@user]` — {frak('Get user information')}
• `/id` — {frak('Get user/chat IDs')}

━━━━━━━━━━━━━━━━━━━━

🛡️ **{frak('Auto-Protections (Always Active)')}**
• ✅ {frak('Slang & illegal word filter (all languages)')}
• ✅ {frak('Illegal media detection & removal')}
• ✅ {frak('Media auto-delete for non-certified members')}
• ✅ {frak('Group name protection & auto-restore')}
• ✅ {frak('Group photo protection & auto-restore')}
""".strip()


START_TEXT = """🤖 **{name}**

{line}

👋 {welcome}, **{user}**!
🎖️ {role}: {role_val}

{line}

🛡️ **{guardian}**
_{description}_

{line}

⚡ _{add_me}_"""


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
                f"**{frak('Owner Command:')}** `/auth {uid}`",
                reply_markup=markup([danger(frak("Unauthorized — Contact Owner"))])
            )
            return

        me = await client.get_me()
        name = message.from_user.first_name or "User"
        role_val = frak("Owner 👑") if is_owner else frak("Authorized User ✅")

        await message.reply(
            f"🤖 **{frak('GuardBot — Group Shield')}**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👋 {frak('Welcome back')}, **{name}**!\n"
            f"🎖️ {frak('Role')}: {role_val}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ **{frak('I am your Group Guardian')}**\n"
            f"_{frak('Protecting your group from hateful content,')}_\n"
            f"_{frak('slang, illegal media, and unauthorized changes.')}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ _{frak('Add me to your group and make me Admin!')}_",
            reply_markup=markup(
                [
                    primary(frak("✦ Help & Commands ✦"), data="show_help"),
                    success(frak("✦ Add to Group ✦"),
                            url=f"https://t.me/{me.username}?startgroup=true")
                ],
                [
                    default(frak("✦ Group Info ✦"), data="show_info"),
                    default(frak("✦ Support ✦"), url="https://t.me/kurigram_chat")
                ]
            )
        )

    @app.on_callback_query(filters.regex("^show_help$"))
    async def cb_help(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.edit(
            HELP_TEXT,
            reply_markup=markup(
                [success(frak("✦ Back to Menu ✦"), data="show_start")]
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
            f"⚡ _{frak('Add me to your group and make me Admin!')}_",
            reply_markup=markup(
                [
                    primary(frak("✦ Help & Commands ✦"), data="show_help"),
                    success(frak("✦ Add to Group ✦"),
                            url=f"https://t.me/{me.username}?startgroup=true")
                ],
                [
                    default(frak("✦ Group Info ✦"), data="show_info"),
                    default(frak("✦ Support ✦"), url="https://t.me/kurigram_chat")
                ]
            )
        )

    @app.on_callback_query(filters.regex("^show_info$"))
    async def cb_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.edit(
            f"ℹ️ **{frak('About GuardBot')}**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🤖 **{frak('Version')}:** 2.0\n"
            f"⚙️ **{frak('Framework')}:** Kurigram (Pyrogram fork)\n"
            f"🐍 **{frak('Language')}:** Python 3.11\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ **{frak('Active Protections')}:**\n"
            f"• ✅ {frak('Slang filter (All languages)')}\n"
            f"• ✅ {frak('Illegal media removal')}\n"
            f"• ✅ {frak('Media auto-delete timer')}\n"
            f"• ✅ {frak('Group name & photo shield')}\n"
            f"• ✅ {frak('Certified member system')}\n"
            f"• ✅ {frak('Full admin command suite')}\n"
            f"• ✅ {frak('Warn system (3 strikes)')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup(
                [success(frak("✦ Back to Menu ✦"), data="show_start"),
                 primary(frak("✦ Commands ✦"), data="show_help")]
            )
        )

    @app.on_message(filters.command("help"))
    async def cmd_help(client: Client, message: Message):
        uid = message.from_user.id
        if not (uid == OWNER_ID or is_authorized(uid)) and message.chat.type.value == "private":
            return
        me = await client.get_me()
        await message.reply(
            HELP_TEXT,
            reply_markup=markup(
                [primary(frak("✦ Add to Group ✦"),
                         url=f"https://t.me/{me.username}?startgroup=true"),
                 success(frak("✦ Back to Menu ✦"), data="show_start")]
            )
        )

    @app.on_callback_query(filters.regex("^noop$"))
    async def cb_noop(client: Client, query: CallbackQuery):
        await query.answer()
