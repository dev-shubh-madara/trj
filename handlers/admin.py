import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, PeerIdInvalid

from config import OWNER_ID
from database import (
    is_authorized, is_certified, add_warn, get_warns, remove_warn, reset_warns
)
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default

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
                f"**{frak('Only admins can use this command.')}**",
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
            return await message.reply(f"**{frak('Reply to a user or give username to ban.')}**",
                                       reply_markup=markup([primary(frak("Usage: /ban @user"))]))
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else (parts[1] if not parts[1].startswith("@") and not parts[1].lstrip("-").isdigit() else "No reason provided")
        try:
            await client.ban_chat_member(message.chat.id, target.id)
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(f"**{frak('Cannot ban this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"🔨 **{frak('User Banned')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"📋 **{frak('Reason')}:** {reason}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([danger(frak("Banned")), success(frak("Action Taken"))])
        )

    @app.on_message(filters.command("unban") & filters.group)
    @_admin_only
    async def cmd_unban(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username to unban.')}**")
        try:
            await client.unban_chat_member(message.chat.id, target.id)
        except Exception:
            return await message.reply(f"**{frak('Cannot unban this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"✅ **{frak('User Unbanned')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([success(frak("Unbanned Successfully"))])
        )

    @app.on_message(filters.command("tban") & filters.group)
    @_admin_only
    async def cmd_tban(client: Client, message: Message):
        parts = message.text.split()
        target = await _get_target(client, message)
        if not target or len(parts) < 3:
            return await message.reply(
                f"**{frak('Usage: /tban @user 1h reason')}**\n"
                f"_Times: 10m, 2h, 1d_",
                reply_markup=markup([primary(frak("Usage: /tban @user time reason"))])
            )
        time_str = parts[2] if message.reply_to_message else parts[2]
        secs = _parse_time(time_str)
        if not secs:
            return await message.reply(f"**{frak('Invalid time. Use: 10m, 2h, 1d')}**")
        until = datetime.now() + timedelta(seconds=secs)
        try:
            await client.ban_chat_member(message.chat.id, target.id, until_date=until)
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(f"**{frak('Cannot ban this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"⏳ **{frak('Temp Ban Applied')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"⏱️ **{frak('Duration')}:** {time_str}\n"
            f"📅 **{frak('Until')}:** {until.strftime('%Y-%m-%d %H:%M')}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([danger(frak("Temp Banned")), success(frak("Auto-Expires"))])
        )

    @app.on_message(filters.command("kick") & filters.group)
    @_admin_only
    async def cmd_kick(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username to kick.')}**")
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "No reason provided"
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            await asyncio.sleep(1)
            await client.unban_chat_member(message.chat.id, target.id)
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(f"**{frak('Cannot kick this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"👢 **{frak('User Kicked')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"📋 **{frak('Reason')}:** {reason}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([danger(frak("Kicked")), primary(frak("Can Rejoin"))])
        )

    @app.on_message(filters.command("mute") & filters.group)
    @_admin_only
    async def cmd_mute(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username to mute.')}**")
        parts = message.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "No reason provided"
        try:
            await client.restrict_chat_member(
                message.chat.id, target.id,
                ChatPermissions(can_send_messages=False)
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(f"**{frak('Cannot mute this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"🔇 **{frak('User Muted')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"📋 **{frak('Reason')}:** {reason}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([danger(frak("Muted")), success(frak("Use /unmute to restore"))])
        )

    @app.on_message(filters.command("unmute") & filters.group)
    @_admin_only
    async def cmd_unmute(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username to unmute.')}**")
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
            return await message.reply(f"**{frak('Cannot unmute this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"🔊 **{frak('User Unmuted')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([success(frak("Unmuted Successfully"))])
        )

    @app.on_message(filters.command("tmute") & filters.group)
    @_admin_only
    async def cmd_tmute(client: Client, message: Message):
        parts = message.text.split()
        target = await _get_target(client, message)
        if not target or len(parts) < 3:
            return await message.reply(
                f"**{frak('Usage: /tmute @user 1h reason')}**",
                reply_markup=markup([primary(frak("Usage: /tmute @user time"))])
            )
        time_str = parts[2] if message.reply_to_message else parts[2]
        secs = _parse_time(time_str)
        if not secs:
            return await message.reply(f"**{frak('Invalid time. Use: 10m, 2h, 1d')}**")
        until = datetime.now() + timedelta(seconds=secs)
        try:
            await client.restrict_chat_member(
                message.chat.id, target.id,
                ChatPermissions(can_send_messages=False),
                until_date=until
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(f"**{frak('Cannot mute this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"⏳ **{frak('Temp Mute Applied')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"⏱️ **{frak('Duration')}:** {time_str}\n"
            f"📅 **{frak('Until')}:** {until.strftime('%Y-%m-%d %H:%M')}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([danger(frak("Temp Muted")), success(frak("Auto-Expires"))])
        )

    @app.on_message(filters.command("warn") & filters.group)
    @_admin_only
    async def cmd_warn(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username to warn.')}**")
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
                f"🚫 **{frak('User Banned — Max Warns Reached')}**\n\n"
                f"👤 **{frak('User')}:** {target.mention}\n"
                f"⚠️ **{frak('Warns')}:** {MAX_WARNS}/{MAX_WARNS}\n"
                f"📋 **{frak('Last Reason')}:** {reason}\n"
                f"🔨 **{frak('Auto-banned for reaching max warnings.')}**",
                reply_markup=markup([danger(frak(f"Auto Banned — {MAX_WARNS} Warns"))])
            )
        await message.reply(
            f"⚠️ **{frak('Warning Issued')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"📋 **{frak('Reason')}:** {reason}\n"
            f"⚠️ **{frak('Warns')}:** {count}/{MAX_WARNS}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}\n\n"
            f"_{frak('Reaching')} {MAX_WARNS} {frak('warns results in an automatic ban.')}_",
            reply_markup=markup(
                [danger(frak(f"Warn {count}/{MAX_WARNS}")), primary(frak("Use /unwarn to remove"))]
            )
        )

    @app.on_message(filters.command("unwarn") & filters.group)
    @_admin_only
    async def cmd_unwarn(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username.')}**")
        new_count = remove_warn(target.id, message.chat.id)
        await message.reply(
            f"✅ **{frak('Warning Removed')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"⚠️ **{frak('Remaining Warns')}:** {new_count}/{MAX_WARNS}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([success(frak("Warn Removed"))])
        )

    @app.on_message(filters.command("warns") & filters.group)
    async def cmd_warns(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            target = message.from_user
        count, reasons = get_warns(target.id, message.chat.id)
        reason_lines = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(reasons)) or "  None"
        await message.reply(
            f"📋 **{frak('Warn Record')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"⚠️ **{frak('Total Warns')}:** {count}/{MAX_WARNS}\n"
            f"📝 **{frak('Reasons')}:**\n{reason_lines}",
            reply_markup=markup(
                [primary(frak(f"{count}/{MAX_WARNS} Warns")),
                 success(frak("Use /unwarn to remove")) if count > 0 else default(frak("No warns"))]
            )
        )

    @app.on_message(filters.command("resetwarns") & filters.group)
    @_admin_only
    async def cmd_reset_warns(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username.')}**")
        reset_warns(target.id, message.chat.id)
        await message.reply(
            f"🔄 **{frak('All Warnings Reset')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"⚠️ **{frak('Warns')}:** 0/{MAX_WARNS}\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([success(frak("Warns Reset"))])
        )

    @app.on_message(filters.command("pin") & filters.group)
    @_admin_only
    async def cmd_pin(client: Client, message: Message):
        if not message.reply_to_message:
            return await message.reply(f"**{frak('Reply to a message to pin it.')}**")
        try:
            await message.reply_to_message.pin(disable_notification=False)
            await message.reply(
                f"📌 **{frak('Message Pinned')}**\n"
                f"👮 **{frak('By')}:** {message.from_user.mention}",
                reply_markup=markup([success(frak("Pinned Successfully"))])
            )
        except Exception:
            await message.reply(f"**{frak('Could not pin message.')}**",
                                reply_markup=markup([danger(frak("Failed"))]))

    @app.on_message(filters.command("unpin") & filters.group)
    @_admin_only
    async def cmd_unpin(client: Client, message: Message):
        try:
            if message.reply_to_message:
                await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
            else:
                await client.unpin_chat_message(message.chat.id)
            await message.reply(
                f"📌 **{frak('Message Unpinned')}**\n"
                f"👮 **{frak('By')}:** {message.from_user.mention}",
                reply_markup=markup([success(frak("Unpinned"))])
            )
        except Exception:
            await message.reply(f"**{frak('Could not unpin message.')}**",
                                reply_markup=markup([danger(frak("Failed"))]))

    @app.on_message(filters.command("unpinall") & filters.group)
    @_admin_only
    async def cmd_unpin_all(client: Client, message: Message):
        try:
            await client.unpin_all_chat_messages(message.chat.id)
            await message.reply(
                f"📌 **{frak('All Messages Unpinned')}**\n"
                f"👮 **{frak('By')}:** {message.from_user.mention}",
                reply_markup=markup([success(frak("All Unpinned"))])
            )
        except Exception:
            await message.reply(f"**{frak('Could not unpin all messages.')}**",
                                reply_markup=markup([danger(frak("Failed"))]))

    @app.on_message(filters.command("promote") & filters.group)
    @_admin_only
    async def cmd_promote(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username to promote.')}**")
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
            return await message.reply(f"**{frak('Cannot promote this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"⭐ **{frak('User Promoted')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([success(frak("Promoted to Admin"))])
        )

    @app.on_message(filters.command("demote") & filters.group)
    @_admin_only
    async def cmd_demote(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            return await message.reply(f"**{frak('Reply to a user or give username to demote.')}**")
        try:
            await client.promote_chat_member(
                message.chat.id, target.id,
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        except (UserAdminInvalid, ChatAdminRequired):
            return await message.reply(f"**{frak('Cannot demote this user.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"🔻 **{frak('User Demoted')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🆔 **ID:** `{target.id}`\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([danger(frak("Demoted")), success(frak("Reverted to Member"))])
        )

    @app.on_message(filters.command("title") & filters.group)
    @_admin_only
    async def cmd_title(client: Client, message: Message):
        parts = message.text.split(None, 2)
        target = await _get_target(client, message)
        if not target:
            return await message.reply(
                f"**{frak('Usage: /title @user Custom Title')}**",
                reply_markup=markup([primary(frak("Reply to user + /title text"))])
            )
        title = parts[-1] if len(parts) > 1 else ""
        if message.reply_to_message and len(parts) > 1:
            title = " ".join(parts[1:])
        if not title:
            return await message.reply(f"**{frak('Provide a title text.')}**")
        try:
            await client.set_administrator_title(message.chat.id, target.id, title[:16])
        except Exception:
            return await message.reply(f"**{frak('Cannot set title. Make sure user is admin.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"🏷️ **{frak('Admin Title Set')}**\n\n"
            f"👤 **{frak('User')}:** {target.mention}\n"
            f"🏷️ **{frak('Title')}:** `{title[:16]}`\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([success(frak(f"Title: {title[:16]}"))])
        )

    @app.on_message(filters.command("del") & filters.group)
    @_admin_only
    async def cmd_del(client: Client, message: Message):
        if not message.reply_to_message:
            return await message.reply(f"**{frak('Reply to a message to delete it.')}**")
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception:
            await message.reply(f"**{frak('Cannot delete that message.')}**",
                                reply_markup=markup([danger(frak("Failed"))]))

    @app.on_message(filters.command("purge") & filters.group)
    @_admin_only
    async def cmd_purge(client: Client, message: Message):
        if not message.reply_to_message:
            return await message.reply(f"**{frak('Reply to a message to start purging from.')}**")
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
            f"🗑️ **{frak('Purge Complete')}**\n\n"
            f"🗑️ **{frak('Deleted')}:** {deleted} messages\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
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
        try:
            await client.set_chat_permissions(
                message.chat.id,
                ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_send_polls=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_change_info=False
                )
            )
        except Exception:
            return await message.reply(f"**{frak('Cannot lock the group.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"🔒 **{frak('Group Locked')}**\n\n"
            f"🚫 **{frak('All members are now restricted.')}**\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}\n\n"
            f"_{frak('Use')} /unlock {frak('to restore permissions.')}_",
            reply_markup=markup([danger(frak("Group Locked")), primary(frak("Use /unlock"))])
        )

    @app.on_message(filters.command("unlock") & filters.group)
    @_admin_only
    async def cmd_unlock(client: Client, message: Message):
        try:
            await client.set_chat_permissions(
                message.chat.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_invite_users=True,
                    can_pin_messages=False,
                    can_change_info=False
                )
            )
        except Exception:
            return await message.reply(f"**{frak('Cannot unlock the group.')}**",
                                       reply_markup=markup([danger(frak("Failed"))]))
        await message.reply(
            f"🔓 **{frak('Group Unlocked')}**\n\n"
            f"✅ **{frak('All members can send messages again.')}**\n"
            f"👮 **{frak('By')}:** {message.from_user.mention}",
            reply_markup=markup([success(frak("Group Unlocked"))])
        )

    @app.on_message(filters.command("info") & filters.group)
    async def cmd_info(client: Client, message: Message):
        target = await _get_target(client, message)
        if not target:
            target = message.from_user
        count, _ = get_warns(target.id, message.chat.id)
        cert = is_certified(target.id, message.chat.id)
        try:
            member = await client.get_chat_member(message.chat.id, target.id)
            status = member.status.value.title()
        except Exception:
            status = "Unknown"
        dc = getattr(target, "dc_id", "N/A")
        await message.reply(
            f"👤 **{frak('User Information')}**\n\n"
            f"📛 **{frak('Name')}:** {target.mention}\n"
            f"🆔 **{frak('User ID')}:** `{target.id}`\n"
            f"🔖 **{frak('Username')}:** @{target.username or 'None'}\n"
            f"🌐 **DC:** {dc}\n"
            f"👮 **{frak('Status')}:** {status}\n"
            f"⭐ **{frak('Certified')}:** {'Yes ✅' if cert else 'No ❌'}\n"
            f"⚠️ **{frak('Warnings')}:** {count}/{MAX_WARNS}",
            reply_markup=markup(
                [primary(frak("Certified ⭐")) if cert else danger(frak("Not Certified")),
                 success(frak(f"Warns: {count}/{MAX_WARNS}"))]
            )
        )

    @app.on_message(filters.command("id") & filters.group)
    async def cmd_id(client: Client, message: Message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        await message.reply(
            f"🆔 **{frak('ID Information')}**\n\n"
            f"👤 **{frak('Your ID')}:** `{message.from_user.id}`\n"
            f"💬 **{frak('Chat ID')}:** `{message.chat.id}`\n"
            + (f"↩️ **{frak('Replied User ID')}:** `{target.id}`\n" if message.reply_to_message else ""),
            reply_markup=markup([primary(frak(f"Chat: {message.chat.id}"))])
        )

    @app.on_message(filters.command("admins") & filters.group)
    async def cmd_admins(client: Client, message: Message):
        admins = []
        async for member in client.get_chat_members(message.chat.id, filter="administrators"):
            if not member.user.is_bot:
                admins.append(f"• {member.user.mention}")
        await message.reply(
            f"👮 **{frak('Group Administrators')}**\n\n" + "\n".join(admins) if admins
            else f"**{frak('No admins found.')}**",
            reply_markup=markup([primary(frak(f"{len(admins)} Admins"))])
        )
