from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from config import OWNER_ID
from database import is_authorized
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default


HELP_TEXT = f"""
🤖 **{frak('GuardBot — Command Center')}**

━━━━━━━━━━━━━━━━━━━━

🔐 **{frak('Owner Commands')}** _(Private)_
• `/auth <id>` — {frak('Authorize a user')}
• `/unauth <id>` — {frak('Remove authorization')}
• `/broadcast` — {frak('Broadcast to all groups (reply)')}

━━━━━━━━━━━━━━━━━━━━

⭐ **{frak('Certification')}** _(Group)_
• `/giveaura` — {frak('Certify a member (reply)')}
• `/removeaura` — {frak('Revoke certification (reply)')}
• `/certified` — {frak('List certified members')}
• `/snapshotgroup` — {frak('Save group name & photo')}

━━━━━━━━━━━━━━━━━━━━

👋 **{frak('Welcome System')}** _(Group)_
• `/setwelcome <text>` — {frak('Set custom welcome message')}
• `/setwelcome off` — {frak('Disable welcome messages')}
• `/welcome` — {frak('Check welcome settings')}
• `{{name}}` `{{first}}` `{{chat}}` `{{id}}` — {frak('Variables')}

━━━━━━━━━━━━━━━━━━━━

🔨 **{frak('Ban & Kick')}** _(Group / Admin)_
• `/ban [@user] [reason]` — {frak('Permanent ban')}
• `/unban [@user]` — {frak('Unban user')}
• `/tban [@user] [time]` — {frak('Temp ban (1h, 2d)')}
• `/kick [@user]` — {frak('Kick (can rejoin)')}

━━━━━━━━━━━━━━━━━━━━

🔇 **{frak('Mute')}** _(Group / Admin)_
• `/mute [@user]` — {frak('Mute user')}
• `/unmute [@user]` — {frak('Unmute user')}
• `/tmute [@user] [time]` — {frak('Temp mute')}

━━━━━━━━━━━━━━━━━━━━

⚠️ **{frak('Warnings')}** _(Group / Admin)_
• `/warn [@user] [reason]` — {frak('Warn user (3 = ban)')}
• `/unwarn [@user]` — {frak('Remove last warn')}
• `/warns [@user]` — {frak('Check warns')}
• `/resetwarns [@user]` — {frak('Reset all warns')}

━━━━━━━━━━━━━━━━━━━━

📌 **{frak('Messages')}** _(Group / Admin)_
• `/pin` — {frak('Pin replied message')}
• `/unpin` — {frak('Unpin message')}
• `/unpinall` — {frak('Unpin all')}
• `/del` — {frak('Delete replied message')}
• `/purge` — {frak('Delete from reply to now')}
• `/clgroup` — {frak('Delete ALL group messages')}

━━━━━━━━━━━━━━━━━━━━

👮 **{frak('Admin')}** _(Group / Admin)_
• `/promote [@user]` — {frak('Promote to admin')}
• `/demote [@user]` — {frak('Demote from admin')}
• `/title [@user] [text]` — {frak('Set admin title')}
• `/admins` — {frak('List admins')}

━━━━━━━━━━━━━━━━━━━━

🔒 **{frak('Group Lock')}** _(Group / Admin)_
• `/lock` — {frak('Lock group')}
• `/unlock` — {frak('Unlock group')}
• `/setgrouppic <10|20|30>` — {frak('Media delete timer')}
• `/groupinfo` — {frak('Group settings')}

━━━━━━━━━━━━━━━━━━━━

📊 **{frak('Info')}**
• `/info [@user]` — {frak('User info')}
• `/id` — {frak('Get IDs')}
• `/start` — {frak('Main menu')}
• `/help` — {frak('This menu')}
""".strip()


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
                reply_markup=markup([danger(frak("✦ Unauthorized ✦"))])
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
                    primary(frak("✦ Group Info ✦"), data="show_info"),
                    danger(frak("✦ Broadcast ✦"), data="show_broadcast")
                ]
            )
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
            f"⚡ _{frak('Add me to your group and make me Admin!')}_",
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
            f"🤖 **{frak('Version')}:** 3.0\n"
            f"⚙️ **{frak('Framework')}:** Kurigram v2.2.23\n"
            f"🐍 **{frak('Language')}:** Python 3.11\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ **{frak('Active Protections')}:**\n"
            f"• ✅ {frak('Slang filter — all languages + bots')}\n"
            f"• ✅ {frak('Illegal media auto-removal')}\n"
            f"• ✅ {frak('Media auto-delete timer')}\n"
            f"• ✅ {frak('Group name & photo shield')}\n"
            f"• ✅ {frak('Certified member system')}\n"
            f"• ✅ {frak('Full admin command suite')}\n"
            f"• ✅ {frak('Warn system (3 strikes = ban)')}\n"
            f"• ✅ {frak('Welcome messages with profile photo')}\n"
            f"• ✅ {frak('Owner broadcast system')}\n"
            f"• ✅ {frak('Group clear command')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
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
            f"_{frak('Go to private chat with me and:')}_ \n\n"
            f"1. {frak('Forward or write the message you want to send')}\n"
            f"2. {frak('Reply to it with')} `/broadcast`\n\n"
            f"📡 {frak('The message will be sent to all groups.')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup(
                [
                    primary(frak("✦ Back to Menu ✦"), data="show_start"),
                    success(frak("✦ How to Broadcast ✦"), data="noop")
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
