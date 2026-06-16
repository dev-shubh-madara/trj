import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ParseMode
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, PeerIdInvalid

from config import OWNER_ID
from database import (
    is_authorized, is_certified, add_warn, get_warns, remove_warn, reset_warns
)
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default
from utils.emojis import em, em_row

PM = ParseMode.HTML
MAX_WARNS = 3


def _parse_time(t: str) -> int:
    unit = t[-1].lower()
    try:
        val = int(t[:-1])
    except ValueError:
        return 0
    return {"m": val*60, "h": val*3600, "d": val*86400}.get(unit, 0)


async def _get_target(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = message.text.split()
    if len(parts) >= 2:
        try:
            return await client.get_users(parts[1])
        except Exception:
            pass
    return None


async def _is_admin(client, chat_id, user_id) -> bool:
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status.value in ("owner", "administrator")
    except Exception:
        return False


def _admin_only(func):
    async def wrapper(client: Client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        if uid != OWNER_ID and not is_authorized(uid):
            return
        if not await _is_admin(client, message.chat.id, uid):
            await message.reply(
                f"{em()} <b>{frak('Admins Only')}</b>\n\n"
                f"{em()} {frak('Only group admins can use this command.')}",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Admins Only"))])
            )
            return
        await func(client, message)
    wrapper.__name__ = func.__name__
    return wrapper


def register(app: Client):

    @app.on_message(filters.command("ban") & filters.group)
    @_admin_only
    async def cmd_ban(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Usage')}</b>\n\n"
                f"{em()} <code>/ban @user reason</code>\n"
                f"{em()} {frak('or reply to a user message')}",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Reply + /ban reason"))])
            )
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "No reason provided"
        try:
            await client.ban_chat_member(message.chat.id, target.id)
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot ban this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(5)}\n\n"
            f"🔨 <b>{frak('User Banned')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Banned")), success(frak("Action Taken"))])
        )

    @app.on_message(filters.command("unban") & filters.group)
    @_admin_only
    async def cmd_unban(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to unban.')}</b>",
                parse_mode=PM
            )
        try:
            await client.unban_chat_member(message.chat.id, target.id)
        except Exception:
            return await message.reply(
                f"{em()} <b>{frak('Cannot unban this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(4)}\n\n"
            f"✅ <b>{frak('User Unbanned')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([success(frak("Unbanned Successfully"))])
        )

    @app.on_message(filters.command("tban") & filters.group)
    @_admin_only
    async def cmd_tban(client: Client, message: Message):
        parts = message.text.split()
        target = await _get_target(client, message)
        if not target or len(parts) < 3:
            return await message.reply(
                f"{em()} <b>{frak('Usage:')}</b> <code>/tban @user 1h reason</code>\n"
                f"{em()} {frak('Times:')} <code>10m</code>, <code>2h</code>, <code>1d</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Usage: /tban @user time reason"))])
            )
        time_str = parts[2]
        secs = _parse_time(time_str)
        if not secs:
            return await message.reply(
                f"{em()} <b>{frak('Invalid time. Use: 10m, 2h, 1d')}</b>",
                parse_mode=PM
            )
        until = datetime.now() + timedelta(seconds=secs)
        try:
            await client.ban_chat_member(message.chat.id, target.id, until_date=until)
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot ban this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(5)}\n\n"
            f"⏳ <b>{frak('Temp Ban Applied')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('Duration:')}</b> <code>{time_str}</code>\n"
            f"{em()} <b>{frak('Until:')}</b> <code>{until.strftime('%Y-%m-%d %H:%M')}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Temp Banned")), success(frak("Auto-Expires"))])
        )

    @app.on_message(filters.command("kick") & filters.group)
    @_admin_only
    async def cmd_kick(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to kick.')}</b>",
                parse_mode=PM
            )
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "No reason provided"
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            await asyncio.sleep(1)
            await client.unban_chat_member(message.chat.id, target.id)
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot kick this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(4)}\n\n"
            f"👢 <b>{frak('User Kicked')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Kicked")), primary(frak("Can Rejoin"))])
        )

    @app.on_message(filters.command("mute") & filters.group)
    @_admin_only
    async def cmd_mute(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to mute.')}</b>",
                parse_mode=PM
            )
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "No reason provided"
        try:
            await client.restrict_chat_member(
                message.chat.id, target.id,
                ChatPermissions(can_send_messages=False)
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot mute this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(4)}\n\n"
            f"🔇 <b>{frak('User Muted')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
            f"{em()} <i>{frak('Use /unmute to restore.')}</i>",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Muted")), success(frak("Use /unmute"))])
        )

    @app.on_message(filters.command("unmute") & filters.group)
    @_admin_only
    async def cmd_unmute(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to unmute.')}</b>",
                parse_mode=PM
            )
        try:
            await client.restrict_chat_member(
                message.chat.id, target.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False
                )
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot unmute this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(4)}\n\n"
            f"🔊 <b>{frak('User Unmuted')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([success(frak("Unmuted Successfully"))])
        )

    @app.on_message(filters.command("tmute") & filters.group)
    @_admin_only
    async def cmd_tmute(client: Client, message: Message):
        parts = message.text.split()
        target = await _get_target(client, message)
        if not target or len(parts) < 3:
            return await message.reply(
                f"{em()} <b>{frak('Usage:')}</b> <code>/tmute @user 1h reason</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Usage: /tmute @user time"))])
            )
        time_str = parts[2]
        secs = _parse_time(time_str)
        if not secs:
            return await message.reply(
                f"{em()} <b>{frak('Invalid time. Use: 10m, 2h, 1d')}</b>",
                parse_mode=PM
            )
        until = datetime.now() + timedelta(seconds=secs)
        try:
            await client.restrict_chat_member(
                message.chat.id, target.id,
                ChatPermissions(can_send_messages=False),
                until_date=until
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot mute this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(5)}\n\n"
            f"⏳ <b>{frak('Temp Mute Applied')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('Duration:')}</b> <code>{time_str}</code>\n"
            f"{em()} <b>{frak('Until:')}</b> <code>{until.strftime('%Y-%m-%d %H:%M')}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Temp Muted")), success(frak("Auto-Expires"))])
        )

    @app.on_message(filters.command("warn") & filters.group)
    @_admin_only
    async def cmd_warn(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to warn.')}</b>",
                parse_mode=PM
            )
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "No reason provided"
        count = add_warn(target.id, message.chat.id, reason)
        if count >= MAX_WARNS:
            reset_warns(target.id, message.chat.id)
            try:
                await client.ban_chat_member(message.chat.id, target.id)
            except Exception:
                pass
            return await message.reply(
                f"{em_row(5)}\n\n"
                f"🚫 <b>{frak('Auto-Ban — Max Warns Reached!')}</b>\n\n"
                f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
                f"{em()} <b>{frak('Warns:')}</b> <code>{MAX_WARNS}/{MAX_WARNS}</code>\n"
                f"{em()} <b>{frak('Last Reason:')}</b> {reason}\n"
                f"{em()} 🔨 {frak('Automatically banned.')}\n\n"
                f"— <b>{frak('Powered by Madara')}</b> 🔥",
                parse_mode=PM,
                reply_markup=markup([danger(frak(f"Auto Banned — {MAX_WARNS} Warns"))])
            )
        bar = "🟥" * count + "⬜" * (MAX_WARNS - count)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"⚠️ <b>{frak('Warning Issued')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n"
            f"{em()} <b>{frak('Warns:')}</b> <code>{count}/{MAX_WARNS}</code> {bar}\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
            f"<i>{frak('Reaching')} {MAX_WARNS} {frak('warns = auto-ban.')}</i>",
            parse_mode=PM,
            reply_markup=markup(
                [danger(frak(f"Warn {count}/{MAX_WARNS}")), primary(frak("Use /unwarn to remove"))]
            )
        )

    @app.on_message(filters.command("unwarn") & filters.group)
    @_admin_only
    async def cmd_unwarn(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user.')}</b>",
                parse_mode=PM
            )
        new_count = remove_warn(target.id, message.chat.id)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"✅ <b>{frak('Warning Removed')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('Remaining Warns:')}</b> <code>{new_count}/{MAX_WARNS}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([success(frak("Warn Removed"))])
        )

    @app.on_message(filters.command("warns") & filters.group)
    async def cmd_warns(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            target = message.from_user
        count, reasons = get_warns(target.id, message.chat.id)
        bar = "🟥" * count + "⬜" * (MAX_WARNS - count)
        reason_lines = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(reasons)) or f"  {frak('None')}"
        await message.reply(
            f"{em_row(4)}\n\n"
            f"📋 <b>{frak('Warn Record')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('Total Warns:')}</b> <code>{count}/{MAX_WARNS}</code> {bar}\n"
            f"{em()} <b>{frak('Reasons:')}</b>\n{reason_lines}",
            parse_mode=PM,
            reply_markup=markup(
                [primary(frak(f"{count}/{MAX_WARNS} Warns")),
                 success(frak("Use /unwarn to remove")) if count > 0 else default(frak("Clean Record"))]
            )
        )

    @app.on_message(filters.command("resetwarns") & filters.group)
    @_admin_only
    async def cmd_reset_warns(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user.')}</b>",
                parse_mode=PM
            )
        reset_warns(target.id, message.chat.id)
        await message.reply(
            f"{em_row(4)}\n\n"
            f"🔄 <b>{frak('All Warnings Reset')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('Warns:')}</b> <code>0/{MAX_WARNS}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([success(frak("Warns Reset"))])
        )

    @app.on_message(filters.command("pin") & filters.group)
    @_admin_only
    async def cmd_pin(client: Client, message: Message):
        if not message.reply_to_message:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a message to pin it.')}</b>",
                parse_mode=PM
            )
        try:
            await message.reply_to_message.pin(disable_notification=False)
            await message.reply(
                f"{em_row(3)}\n\n"
                f"📌 <b>{frak('Message Pinned!')}</b>\n"
                f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
                parse_mode=PM,
                reply_markup=markup([success(frak("Pinned Successfully"))])
            )
        except Exception:
            await message.reply(
                f"{em()} <b>{frak('Could not pin message.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

    @app.on_message(filters.command("unpin") & filters.group)
    @_admin_only
    async def cmd_unpin(client: Client, message: Message):
        try:
            if message.reply_to_message:
                await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
            else:
                await client.unpin_chat_message(message.chat.id)
            await message.reply(
                f"{em()} <b>{frak('Message Unpinned')}</b>\n"
                f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
                parse_mode=PM,
                reply_markup=markup([success(frak("Unpinned"))])
            )
        except Exception:
            await message.reply(
                f"{em()} <b>{frak('Could not unpin.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

    @app.on_message(filters.command("unpinall") & filters.group)
    @_admin_only
    async def cmd_unpin_all(client: Client, message: Message):
        try:
            await client.unpin_all_chat_messages(message.chat.id)
            await message.reply(
                f"{em()} <b>{frak('All Messages Unpinned')}</b>\n"
                f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
                parse_mode=PM,
                reply_markup=markup([success(frak("All Unpinned"))])
            )
        except Exception:
            await message.reply(
                f"{em()} <b>{frak('Could not unpin all.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

    @app.on_message(filters.command("promote") & filters.group)
    @_admin_only
    async def cmd_promote(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to promote.')}</b>",
                parse_mode=PM
            )
        try:
            await client.promote_chat_member(
                message.chat.id, target.id,
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot promote this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(5)}\n\n"
            f"⭐ <b>{frak('User Promoted!')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([success(frak("Promoted to Admin"))])
        )

    @app.on_message(filters.command("demote") & filters.group)
    @_admin_only
    async def cmd_demote(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to demote.')}</b>",
                parse_mode=PM
            )
        try:
            await client.promote_chat_member(
                message.chat.id, target.id,
                can_manage_chat=False, can_delete_messages=False,
                can_manage_video_chats=False, can_restrict_members=False,
                can_promote_members=False, can_change_info=False,
                can_invite_users=False, can_pin_messages=False
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot demote this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(3)}\n\n"
            f"🔻 <b>{frak('User Demoted')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Demoted")), success(frak("Reverted to Member"))])
        )

    @app.on_message(filters.command("title") & filters.group)
    @_admin_only
    async def cmd_title(client: Client, message: Message):
        parts = message.text.split(None, 2)
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Usage:')}</b> <code>/title @user Custom Title</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Reply to user + /title text"))])
            )
        title = " ".join(parts[1:]) if len(parts) > 1 else ""
        if message.reply_to_message and len(parts) > 1:
            title = " ".join(parts[1:])
        if not title:
            return await message.reply(
                f"{em()} <b>{frak('Provide a title text.')}</b>",
                parse_mode=PM
            )
        try:
            await client.set_administrator_title(message.chat.id, target.id, title[:16])
        except Exception:
            return await message.reply(
                f"{em()} <b>{frak('Cannot set title. Make sure user is admin.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(3)}\n\n"
            f"🏷️ <b>{frak('Admin Title Set!')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('Title:')}</b> <code>{title[:16]}</code>\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([success(frak(f"Title: {title[:16]}"))])
        )

    @app.on_message(filters.command("del") & filters.group)
    @_admin_only
    async def cmd_del(client: Client, message: Message):
        if not message.reply_to_message:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a message to delete it.')}</b>",
                parse_mode=PM
            )
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception:
            await message.reply(
                f"{em()} <b>{frak('Cannot delete that message.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

    @app.on_message(filters.command("purge") & filters.group)
    @_admin_only
    async def cmd_purge(client: Client, message: Message):
        if not message.reply_to_message:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a message to start purging from.')}</b>",
                parse_mode=PM
            )
        start_id = message.reply_to_message.id
        end_id = message.id
        ids = list(range(start_id, end_id + 1))
        deleted = 0
        for i in range(0, len(ids), 100):
            chunk = ids[i:i+100]
            try:
                await client.delete_messages(message.chat.id, chunk)
                deleted += len(chunk)
            except Exception:
                pass
        note = await client.send_message(
            message.chat.id,
            f"{em_row(3)}\n\n"
            f"🗑️ <b>{frak('Purge Complete!')}</b>\n\n"
            f"{em()} <b>{frak('Deleted:')}</b> <code>{deleted}</code> {frak('messages')}\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup([success(frak(f"Purged {deleted} msgs"))])
        )
        await asyncio.sleep(5)
        try:
            await note.delete()
        except Exception:
            pass

    @app.on_message(filters.command("lock") & filters.group)
    @_admin_only
    async def cmd_lock(client: Client, message: Message):
        parts = message.text.split()
        lock_type = parts[1].lower() if len(parts) > 1 else "all"
        try:
            if lock_type in ("all", "chat"):
                perms = ChatPermissions(
                    can_send_messages=False, can_send_media_messages=False,
                    can_send_other_messages=False, can_add_web_page_previews=False,
                    can_send_polls=False
                )
            elif lock_type in ("media", "photo", "video"):
                perms = ChatPermissions(
                    can_send_messages=True, can_send_media_messages=False,
                    can_send_other_messages=False, can_add_web_page_previews=False,
                    can_send_polls=False
                )
            elif lock_type in ("sticker", "gif", "stickers"):
                perms = ChatPermissions(
                    can_send_messages=True, can_send_media_messages=True,
                    can_send_other_messages=False
                )
            else:
                perms = ChatPermissions(
                    can_send_messages=False, can_send_media_messages=False,
                    can_send_other_messages=False, can_add_web_page_previews=False,
                    can_send_polls=False
                )
            await client.set_chat_permissions(message.chat.id, perms)
            await message.reply(
                f"{em_row(4)}\n\n"
                f"🔒 <b>{frak('Group Locked!')}</b>\n\n"
                f"{em()} <b>{frak('Type:')}</b> <code>{lock_type}</code>\n"
                f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
                f"<i>{frak('Use /unlock to restore.')}</i>",
                parse_mode=PM,
                reply_markup=markup([danger(frak(f"Locked: {lock_type}")), primary(frak("Use /unlock"))])
            )
        except Exception:
            await message.reply(
                f"{em()} <b>{frak('Cannot lock group.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

    @app.on_message(filters.command("unlock") & filters.group)
    @_admin_only
    async def cmd_unlock(client: Client, message: Message):
        try:
            await client.set_chat_permissions(
                message.chat.id,
                ChatPermissions(
                    can_send_messages=True, can_send_media_messages=True,
                    can_send_other_messages=True, can_add_web_page_previews=True,
                    can_send_polls=True, can_invite_users=True
                )
            )
            await message.reply(
                f"{em_row(4)}\n\n"
                f"🔓 <b>{frak('Group Unlocked!')}</b>\n\n"
                f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n"
                f"{em()} {frak('Members can send messages again.')}",
                parse_mode=PM,
                reply_markup=markup([success(frak("Unlocked")), danger(frak("Use /lock to re-lock"))])
            )
        except Exception:
            await message.reply(
                f"{em()} <b>{frak('Cannot unlock group.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )

    @app.on_message(filters.command("ro") & filters.group)
    @_admin_only
    async def cmd_ro(client: Client, message: Message):
        """Read-only: restrict user from sending any message."""
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to set read-only.')}</b>",
                parse_mode=PM
            )
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "No reason provided"
        try:
            await client.restrict_chat_member(
                message.chat.id, target.id,
                ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_send_polls=False
                )
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot restrict this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(4)}\n\n"
            f"📖 <b>{frak('Read-Only Mode Applied')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('Reason:')}</b> {reason}\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}\n\n"
            f"<i>{frak('User can read but not send. Use /unro to restore.')}</i>",
            parse_mode=PM,
            reply_markup=markup([danger(frak("Read-Only")), primary(frak("Use /unro"))])
        )

    @app.on_message(filters.command("unro") & filters.group)
    @_admin_only
    async def cmd_unro(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"{em()} <b>{frak('Reply to a user to remove read-only.')}</b>",
                parse_mode=PM
            )
        try:
            await client.restrict_chat_member(
                message.chat.id, target.id,
                ChatPermissions(
                    can_send_messages=True, can_send_media_messages=True,
                    can_send_other_messages=True, can_add_web_page_previews=True,
                    can_send_polls=True, can_invite_users=True
                )
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(
                f"{em()} <b>{frak('Cannot unrestrict this user.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Failed"))])
            )
        await message.reply(
            f"{em_row(3)}\n\n"
            f"✅ <b>{frak('Read-Only Removed')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>{frak('By:')}</b> {message.from_user.mention}",
            parse_mode=PM,
            reply_markup=markup([success(frak("Restored Full Access"))])
        )
