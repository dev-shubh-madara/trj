"""
Extra group management tools:
/report   — report a user to admins (sends them a PM alert)
/admins   — list all admins in the group
/invite   — generate a fresh invite link
/id       — show your ID or a replied user's ID
/info     — detailed user info (ID, warns, certified status)
/afk      — mark yourself AFK (auto-reply when mentioned)
/unafk    — remove AFK status
"""
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import ChatAdminRequired

from config import OWNER_ID
from database import is_authorized, get_warns, is_certified, get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, em_row

PM = ParseMode.HTML

_afk: dict[int, str] = {}


def register(app: Client):

    @app.on_message(filters.command("report") & filters.group)
    async def cmd_report(client: Client, message: Message):
        """Members report a user → bot PMs all admins."""
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a message to report that user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Reply + /report"))])
            )

        reporter = message.from_user
        target = message.reply_to_message.from_user
        parts = message.text.split(None, 1)
        reason = parts[1].strip() if len(parts) > 1 else "No reason given"
        chat = message.chat

        alert = (
            f"{em_row(5)}\n\n"
            f"🚨 <b>{frak('User Reported!')}</b>\n\n"
            f"{em()} <b>{frak('Group:')}</b> <code>{chat.title}</code> (<code>{chat.id}</code>)\n"
            f"{em()} <b>{frak('Reported user:')}</b> {target.mention} (<code>{target.id}</code>)\n"
            f"{em()} <b>{frak('Reported by:')}</b> {reporter.mention} (<code>{reporter.id}</code>)\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n\n"
            f"<a href='https://t.me/c/{str(chat.id).replace('-100','')}/{message.reply_to_message.id}'>"
            f"{frak('→ Jump to message')}</a>\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥"
        )
        kb = markup(
            [danger(frak("Ban")), primary(frak("Mute")), success(frak("Dismiss"))]
        )

        try:
            admins = await client.get_chat_members(
                chat.id, filter="administrators"
            )
            notified = 0
            for admin in admins:
                if admin.user.is_bot:
                    continue
                try:
                    await client.send_message(admin.user.id, alert, parse_mode=PM, reply_markup=kb)
                    notified += 1
                except Exception:
                    pass
        except Exception:
            notified = 0

        await message.reply(
            f"{em_row(4)}\n\n"
            f"🚨 <b>{frak('Report Sent!')}</b>\n\n"
            f"{em()} <b>{frak('Reported:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n"
            f"{em()} <b>{frak('Admins notified:')}</b> <code>{notified}</code>\n\n"
            f"<i>{frak('Admins have been alerted privately.')}</i>",
            parse_mode=PM,
            reply_markup=markup([success(frak("✦ Report Filed ✦"))])
        )

    @app.on_message(filters.command("admins") & filters.group)
    async def cmd_admins(client: Client, message: Message):
        """List all admins in the group."""
        try:
            admins = await client.get_chat_members(
                message.chat.id, filter="administrators"
            )
        except Exception:
            return await message.reply(
                f"{em()} <b>{frak('Could not fetch admins.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

        lines = [f"{em_row(5)}\n\n👮 <b>{frak('Group Admins')}</b>\n"]
        for a in admins:
            if a.user.is_bot:
                icon = "🤖"
            elif a.status == ChatMemberStatus.OWNER:
                icon = "👑"
            else:
                icon = "⭐"
            title = f" <i>({a.custom_title})</i>" if a.custom_title else ""
            lines.append(f"{em()} {icon} {a.user.mention}{title}")

        lines.append(f"\n<i>{frak('Total:')} {len(admins)}</i>")
        await message.reply(
            "\n".join(lines),
            parse_mode=PM,
            reply_markup=markup([success(frak(f"✦ {len(admins)} Admins ✦"))])
        )

    @app.on_message(filters.command("invite") & filters.group)
    async def cmd_invite(client: Client, message: Message):
        """Generate a fresh invite link."""
        uid = message.from_user.id
        if uid != OWNER_ID and not is_authorized(uid):
            return
        try:
            link = await client.create_chat_invite_link(
                message.chat.id, creates_join_request=False
            )
            await message.reply(
                f"{em_row(4)}\n\n"
                f"🔗 <b>{frak('Invite Link Generated!')}</b>\n\n"
                f"{em()} <b>{frak('Group:')}</b> <code>{message.chat.title}</code>\n"
                f"{em()} <b>{frak('Link:')}</b> {link.invite_link}\n\n"
                f"<i>{frak('Share this link to invite new members.')}</i>",
                parse_mode=PM,
                reply_markup=markup([success(frak("✦ Copy Link ✦")), primary(frak("✦ /invite ✦"))])
            )
        except ChatAdminRequired:
            await message.reply(
                f"{em()} <b>{frak('Bot needs Invite Users permission.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Missing Permission"))])
            )
        except Exception as e:
            await message.reply(
                f"{em()} <b>{frak('Could not create invite link.')}</b>\n<code>{e}</code>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

    @app.on_message(filters.command("id"))
    async def cmd_id(client: Client, message: Message):
        """Get your or replied user's Telegram ID."""
        if message.reply_to_message and message.reply_to_message.from_user:
            u = message.reply_to_message.from_user
            await message.reply(
                f"{em_row(3)}\n\n"
                f"🆔 <b>{frak('User ID Info')}</b>\n\n"
                f"{em()} <b>{frak('User:')}</b> {u.mention}\n"
                f"{em()} <b>{frak('User ID:')}</b> <code>{u.id}</code>\n"
                f"{em()} <b>{frak('Username:')}</b> @{u.username or frak('None')}\n"
                f"{em()} <b>{frak('Bot:')}</b> {'✅' if u.is_bot else '❌'}",
                parse_mode=PM,
                reply_markup=markup([primary(frak(f"ID: {u.id}"))])
            )
        else:
            u = message.from_user
            chat_id_part = (
                f"\n{em()} <b>{frak('Chat ID:')}</b> <code>{message.chat.id}</code>"
                if message.chat.id != u.id else ""
            )
            await message.reply(
                f"{em_row(3)}\n\n"
                f"🆔 <b>{frak('Your ID')}</b>\n\n"
                f"{em()} <b>{frak('User:')}</b> {u.mention}\n"
                f"{em()} <b>{frak('User ID:')}</b> <code>{u.id}</code>\n"
                f"{em()} <b>{frak('Username:')}</b> @{u.username or frak('None')}"
                f"{chat_id_part}",
                parse_mode=PM,
                reply_markup=markup([primary(frak(f"Your ID: {u.id}"))])
            )

    @app.on_message(filters.command("info") & filters.group)
    async def cmd_info(client: Client, message: Message):
        """Detailed user info with warns + certified status."""
        if message.reply_to_message and message.reply_to_message.from_user:
            u = message.reply_to_message.from_user
        else:
            parts = message.text.split()
            if len(parts) >= 2:
                try:
                    u = await client.get_users(parts[1])
                except Exception:
                    return await message.reply(
                        f"{em()} <b>{frak('User not found.')}</b>",
                        parse_mode=PM
                    )
            else:
                u = message.from_user

        chat_id = message.chat.id
        warns_count, _ = get_warns(u.id, chat_id)
        certified = is_certified(u.id, chat_id)
        authorized = is_authorized(u.id)
        is_owner = u.id == OWNER_ID

        try:
            member = await client.get_chat_member(chat_id, u.id)
            status = member.status.value.title()
            is_admin = member.status.value in ("owner", "administrator")
        except Exception:
            status = frak("Unknown")
            is_admin = False

        role = (
            f"👑 {frak('Owner')}" if is_owner
            else f"⭐ {frak('Certified')}" if certified
            else f"👮 {frak('Admin')}" if is_admin
            else f"✅ {frak('Authorized')}" if authorized
            else f"👤 {frak('Member')}"
        )

        await message.reply(
            f"{em_row(5)}\n\n"
            f"👤 <b>{frak('User Info')}</b>\n\n"
            f"{em()} <b>{frak('Name:')}</b> {u.first_name or ''} {u.last_name or ''}\n"
            f"{em()} <b>{frak('Mention:')}</b> {u.mention}\n"
            f"{em()} <b>ID:</b> <code>{u.id}</code>\n"
            f"{em()} <b>{frak('Username:')}</b> @{u.username or frak('None')}\n"
            f"{em()} <b>{frak('Bot:')}</b> {'✅' if u.is_bot else '❌'}\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{em()} <b>{frak('Status:')}</b> {status}\n"
            f"{em()} <b>{frak('Role:')}</b> {role}\n"
            f"{em()} <b>{frak('Warns:')}</b> <code>{warns_count}/3</code>\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup([
                success(frak(f"✦ {role} ✦")),
                danger(frak(f"⚠️ {warns_count}/3 Warns")) if warns_count > 0
                else primary(frak("✦ Clean Record ✦"))
            ])
        )

    @app.on_message(filters.command("afk") & filters.group)
    async def cmd_afk(client: Client, message: Message):
        """Mark yourself as AFK."""
        uid = message.from_user.id
        parts = message.text.split(None, 1)
        reason = parts[1].strip() if len(parts) > 1 else frak("AFK")
        _afk[uid] = reason
        await message.reply(
            f"{em_row(3)}\n\n"
            f"💤 <b>{frak('AFK Mode Enabled')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {message.from_user.mention}\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n\n"
            f"<i>{frak('You will auto-reply when mentioned. Use /unafk to return.')}</i>",
            parse_mode=PM,
            reply_markup=markup([danger(frak("💤 AFK")), primary(frak("Use /unafk to return"))])
        )

    @app.on_message(filters.command("unafk") & filters.group)
    async def cmd_unafk(client: Client, message: Message):
        """Remove AFK status."""
        uid = message.from_user.id
        if uid not in _afk:
            return await message.reply(
                f"{em()} <b>{frak('You are not AFK.')}</b>",
                parse_mode=PM
            )
        del _afk[uid]
        await message.reply(
            f"{em_row(3)}\n\n"
            f"✅ <b>{frak('Welcome back!')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {message.from_user.mention}\n"
            f"{em()} {frak('AFK status removed.')}",
            parse_mode=PM,
            reply_markup=markup([success(frak("✦ Back Online ✦"))])
        )

    @app.on_message(filters.text & filters.group & filters.mentioned, group=6)
    async def afk_mention_reply(client: Client, message: Message):
        """Auto-reply when an AFK user is mentioned."""
        if not message.from_user:
            return
        mentioned_ids = set()
        if message.reply_to_message and message.reply_to_message.from_user:
            mentioned_ids.add(message.reply_to_message.from_user.id)
        if message.entities:
            for ent in message.entities:
                if ent.type.value == "mention":
                    uname = message.text[ent.offset+1:ent.offset+ent.length]
                    try:
                        u = await client.get_users(uname)
                        mentioned_ids.add(u.id)
                    except Exception:
                        pass
                elif ent.type.value == "text_mention" and ent.user:
                    mentioned_ids.add(ent.user.id)

        for uid in mentioned_ids:
            if uid in _afk:
                reason = _afk[uid]
                try:
                    u = await client.get_users(uid)
                    await message.reply(
                        f"{em()} 💤 <b>{u.first_name}</b> {frak('is currently AFK')}\n"
                        f"{em()} <b>{frak('Reason:')}</b> {reason}",
                        parse_mode=PM
                    )
                except Exception:
                    pass
                break
