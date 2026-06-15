from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from database import add_certified_user, remove_certified_user, is_certified, is_authorized, get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default


def register(app: Client):

    @app.on_message(filters.command("giveaura") & filters.group)
    async def cmd_give_aura(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            await message.reply(
                f"⛔ **{frak('Not Authorized')}**\n{frak('You are not authorized to use this bot.')}",
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        chat_member = await client.get_chat_member(chat_id, user.id)
        if chat_member.status.value not in ("owner", "administrator"):
            await message.reply(
                f"⛔ **{frak('You must be a group admin to certify members.')}**",
                reply_markup=markup([danger(frak("Admins Only"))])
            )
            return

        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply(
                f"❓ **{frak('Usage:')}** {frak('Reply to a user message and use')} `/giveaura`",
                reply_markup=markup([primary(frak("Reply to a user first"))])
            )
            return

        target = message.reply_to_message.from_user

        if is_certified(target.id, chat_id):
            await message.reply(
                f"ℹ️ **{frak('Already Certified')}**\n\n"
                f"👤 {target.mention} {frak('is already a certified member.')}",
                reply_markup=markup([success(frak("Already Certified ⭐"))])
            )
            return

        add_certified_user(target.id, chat_id)

        try:
            await client.promote_chat_member(
                chat_id, target.id,
                can_manage_chat=True,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
        except Exception:
            pass

        await message.reply(
            f"⭐ **{frak('Aura Granted — Certified Member!')}**\n\n"
            f"👤 **{frak('User:')}** {target.mention}\n"
            f"🆔 **{frak('ID:')}** `{target.id}`\n"
            f"🛡️ **{frak('Status:')}** {frak('Certified — Exempt from all restrictions')}\n"
            f"👮 **{frak('Role:')}** {frak('Promoted to Admin')}\n\n"
            f"✨ _{frak('This member is now trusted and certified.')}_",
            reply_markup=markup([success(frak("Certified Member ⭐")), primary(frak("Admin Granted"))])
        )

    @app.on_message(filters.command("removeaura") & filters.group)
    async def cmd_remove_aura(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            await message.reply(
                f"⛔ **{frak('Not Authorized')}**",
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        chat_member = await client.get_chat_member(chat_id, user.id)
        if chat_member.status.value not in ("owner", "administrator"):
            await message.reply(
                f"⛔ **{frak('You must be a group admin.')}**",
                reply_markup=markup([danger(frak("Admins Only"))])
            )
            return

        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply(
                f"❓ **{frak('Usage:')}** {frak('Reply to a user message and use')} `/removeaura`",
                reply_markup=markup([primary(frak("Reply to a user first"))])
            )
            return

        target = message.reply_to_message.from_user
        remove_certified_user(target.id, chat_id)

        await message.reply(
            f"🔴 **{frak('Certification Revoked')}**\n\n"
            f"👤 **{frak('User:')}** {target.mention}\n"
            f"🆔 **{frak('ID:')}** `{target.id}`\n"
            f"🛡️ **{frak('Status:')}** {frak('No longer certified')}\n\n"
            f"⚠️ _{frak('This member is now subject to all group rules.')}_",
            reply_markup=markup([danger(frak("Certification Removed"))])
        )

    @app.on_message(filters.command("certified") & filters.group)
    async def cmd_list_certified(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            return

        conn = get_conn()
        rows = conn.execute(
            "SELECT user_id FROM certified_users WHERE chat_id = ?", (chat_id,)
        ).fetchall()

        if not rows:
            await message.reply(
                f"📋 **{frak('No certified members yet.')}**\n\n{frak('Use')} `/giveaura` {frak('to certify a member.')}",
                reply_markup=markup([primary(frak("Use /giveaura"))])
            )
            return

        lines = [f"⭐ **{frak('Certified Members')}:**\n"]
        for i, row in enumerate(rows, 1):
            try:
                member = await client.get_chat_member(chat_id, row["user_id"])
                name = member.user.mention if member.user else f"`{row['user_id']}`"
            except Exception:
                name = f"`{row['user_id']}`"
            lines.append(f"{i}. {name}")

        await message.reply(
            "\n".join(lines),
            reply_markup=markup([success(frak(f"{len(rows)} Certified Members ⭐"))])
        )
