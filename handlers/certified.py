from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from config import OWNER_ID
from database import add_certified_user, remove_certified_user, is_certified, is_authorized, get_conn
from utils.font import frak
from utils.buttons import markup, primary, success, danger, default
from utils.emojis import em, em_row

PM = ParseMode.HTML


def register(app: Client):

    @app.on_message(filters.command("giveaura") & filters.group)
    async def cmd_give_aura(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            await message.reply(
                f"{em()} ⛔ <b>{frak('Not Authorized')}</b>\n"
                f"{frak('You are not authorized to use this bot.')}",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        chat_member = await client.get_chat_member(chat_id, user.id)
        if chat_member.status.value not in ("owner", "administrator"):
            await message.reply(
                f"{em()} ⛔ <b>{frak('Admins Only')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Admins Only"))])
            )
            return

        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply(
                f"{em()} ❓ <b>{frak('Reply to a user message with')}</b> <code>/giveaura</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Reply to a user first"))])
            )
            return

        target = message.reply_to_message.from_user

        if is_certified(target.id, chat_id):
            await message.reply(
                f"{em_row(3)}\n\n"
                f"ℹ️ <b>{frak('Already Certified')}</b>\n\n"
                f"{em()} {target.mention} {frak('already has an aura.')}",
                parse_mode=PM,
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
            f"{em_row(6)}\n\n"
            f"⭐ <b>{frak('Aura Granted!')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('Status:')}</b> {frak('Certified — Exempt from all restrictions')}\n"
            f"{em()} <b>{frak('Role:')}</b> {frak('Promoted to Admin')}\n\n"
            f"<i>✨ {frak('This member is now trusted and certified.')}</i>\n\n"
            f"— <b>{frak('Powered by Madara')}</b> 🔥",
            parse_mode=PM,
            reply_markup=markup([success(frak("Certified Member ⭐")), primary(frak("Admin Granted"))])
        )

    @app.on_message(filters.command("removeaura") & filters.group)
    async def cmd_remove_aura(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if user.id != OWNER_ID and not is_authorized(user.id):
            await message.reply(
                f"{em()} ⛔ <b>{frak('Not Authorized')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Unauthorized"))])
            )
            return

        chat_member = await client.get_chat_member(chat_id, user.id)
        if chat_member.status.value not in ("owner", "administrator"):
            await message.reply(
                f"{em()} ⛔ <b>{frak('You must be a group admin.')}</b>",
                parse_mode=PM,
                reply_markup=markup([danger(frak("Admins Only"))])
            )
            return

        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply(
                f"{em()} ❓ <b>{frak('Reply to a user message with')}</b> <code>/removeaura</code>",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Reply to a user first"))])
            )
            return

        target = message.reply_to_message.from_user
        remove_certified_user(target.id, chat_id)

        await message.reply(
            f"{em_row(3)}\n\n"
            f"🔴 <b>{frak('Certification Revoked')}</b>\n\n"
            f"{em()} <b>{frak('User:')}</b> {target.mention}\n"
            f"{em()} <b>ID:</b> <code>{target.id}</code>\n"
            f"{em()} <b>{frak('Status:')}</b> {frak('No longer certified')}\n\n"
            f"⚠️ <i>{frak('This member is now subject to all group rules.')}</i>",
            parse_mode=PM,
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
                f"{em_row(3)}\n\n"
                f"📋 <b>{frak('No certified members yet.')}</b>\n\n"
                f"{em()} {frak('Use')} <code>/giveaura</code> {frak('to certify a member.')}",
                parse_mode=PM,
                reply_markup=markup([primary(frak("Use /giveaura"))])
            )
            return

        lines = [f"{em_row(4)}\n\n⭐ <b>{frak('Certified Members:')}</b>\n"]
        for i, row in enumerate(rows, 1):
            try:
                member = await client.get_chat_member(chat_id, row["user_id"])
                name = member.user.mention if member.user else f"<code>{row['user_id']}</code>"
            except Exception:
                name = f"<code>{row['user_id']}</code>"
            lines.append(f"{em()} {i}. {name}")

        await message.reply(
            "\n".join(lines),
            parse_mode=PM,
            reply_markup=markup([success(frak(f"{len(rows)} Certified Members ⭐"))])
        )
