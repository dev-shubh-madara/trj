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


async def _get_random_sticker(client: Client):
    global _sticker_cache
    if not _sticker_cache:
        try:
            ss = await client.get_sticker_set(STICKER_SET)
            _sticker_cache = [s.file_id for s in ss.stickers]
        except Exception:
            return None
    return random.choice(_sticker_cache) if _sticker_cache else None


def _main_menu_kb(me_username: str):
    return markup(
        [
            success(frak("⭐ Certification"), data="help_certified"),
            primary(frak("👋 Welcome"), data="help_welcome"),
        ],
        [
            primary(frak("📝 Notes"), data="help_notes"),
            success(frak("📜 Rules"), data="help_rules"),
        ],
        [
            primary(frak("🔍 Filters"), data="help_filters"),
            danger(frak("🌊 Anti-Flood"), data="help_flood"),
        ],
        [
            danger(frak("🔨 Ban / Kick"), data="help_ban"),
            danger(frak("🔇 Mute"), data="help_mute"),
        ],
        [
            danger(frak("⚠️ Warns"), data="help_warns"),
            primary(frak("📌 Messages"), data="help_messages"),
        ],
        [
            success(frak("👮 Promote / Demote"), data="help_promote"),
            primary(frak("🔒 Group"), data="help_group"),
        ],
        [
            primary(frak("📊 Info / Ping"), data="help_info"),
            danger(frak("📢 Broadcast"), data="help_broadcast"),
        ],
        [
            success(frak("✦ Add to Group ✦"),
                    url=f"https://t.me/{me_username}?startgroup=true"),
        ],
    )


BACK_ROW = [danger(frak("← Back"), data="help_main")]


CATEGORY_CONTENT = {
    "help_certified": (
        f"⭐ **{frak('Certification Commands')}**\n\n"
        f"_{frak('Certified members bypass all filters and get admin rights.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/giveaura"), data="cmd_giveaura"),
             success(frak("/removeaura"), data="cmd_removeaura")],
            [primary(frak("/certified"), data="cmd_certified"),
             primary(frak("/snapshotgroup"), data="cmd_snapshotgroup")],
            [success(frak("/approve"), data="cmd_approve"),
             danger(frak("/unapprove"), data="cmd_unapprove")],
            BACK_ROW,
        )
    ),
    "help_welcome": (
        f"👋 **{frak('Welcome System')}**\n\n"
        f"_{frak('Auto-welcome new members with their profile photo.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/setwelcome <text>"), data="cmd_setwelcome")],
            [danger(frak("/setwelcome off"), data="cmd_setwelcome_off")],
            [primary(frak("/welcome"), data="cmd_welcome")],
            [primary(frak("{name}  {first}  {chat}  {id}"),
                     data="cmd_welcome_vars")],
            BACK_ROW,
        )
    ),
    "help_notes": (
        f"📝 **{frak('Notes System')}**\n\n"
        f"_{frak('Save and retrieve notes. Use #notename in chat to get a note.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/save name text"), data="cmd_save"),
             primary(frak("/get name"), data="cmd_get")],
            [success(frak("/notes"), data="cmd_notes"),
             danger(frak("/clear name"), data="cmd_clear")],
            [danger(frak("/clearall"), data="cmd_clearall"),
             primary(frak("#notename"), data="cmd_hashtag")],
            BACK_ROW,
        )
    ),
    "help_rules": (
        f"📜 **{frak('Rules System')}**\n\n"
        f"_{frak('Set and display group rules.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/setrules <text>"), data="cmd_setrules")],
            [primary(frak("/rules"), data="cmd_rules"),
             danger(frak("/resetrules"), data="cmd_resetrules")],
            BACK_ROW,
        )
    ),
    "help_filters": (
        f"🔍 **{frak('Auto Filter System')}**\n\n"
        f"_{frak('Auto-reply when keywords are detected in messages.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/filter keyword reply"), data="cmd_filter")],
            [primary(frak("/filters"), data="cmd_filters"),
             danger(frak("/stop keyword"), data="cmd_stop")],
            [danger(frak("/stopall"), data="cmd_stopall")],
            BACK_ROW,
        )
    ),
    "help_flood": (
        f"🌊 **{frak('Anti-Flood System')}**\n\n"
        f"_{frak('Auto-mute users who send too many messages too fast.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/setflood <num>"), data="cmd_setflood")],
            [primary(frak("/flood"), data="cmd_flood"),
             danger(frak("/setflood 0  (off)"), data="cmd_setflood_off")],
            BACK_ROW,
        )
    ),
    "help_ban": (
        f"🔨 **{frak('Ban & Kick Commands')}**\n\n"
        f"_{frak('Reply to a user message to target them.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [danger(frak("/ban"), data="cmd_ban"),
             success(frak("/unban"), data="cmd_unban")],
            [danger(frak("/tban <1h/2d>"), data="cmd_tban"),
             danger(frak("/kick"), data="cmd_kick")],
            BACK_ROW,
        )
    ),
    "help_mute": (
        f"🔇 **{frak('Mute Commands')}**\n\n"
        f"_{frak('Reply to a user message to target them.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [danger(frak("/mute"), data="cmd_mute"),
             success(frak("/unmute"), data="cmd_unmute")],
            [danger(frak("/tmute <1h/2d>"), data="cmd_tmute")],
            BACK_ROW,
        )
    ),
    "help_warns": (
        f"⚠️ **{frak('Warn System')}**\n\n"
        f"_{frak('3 warnings = auto-ban. Reply to target user.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [danger(frak("/warn [reason]"), data="cmd_warn"),
             success(frak("/unwarn"), data="cmd_unwarn")],
            [primary(frak("/warns"), data="cmd_warns"),
             danger(frak("/resetwarns"), data="cmd_resetwarns")],
            BACK_ROW,
        )
    ),
    "help_messages": (
        f"📌 **{frak('Message Commands')}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/pin"), data="cmd_pin"),
             danger(frak("/unpin"), data="cmd_unpin")],
            [danger(frak("/unpinall"), data="cmd_unpinall"),
             danger(frak("/del"), data="cmd_del")],
            [danger(frak("/purge"), data="cmd_purge"),
             danger(frak("/clgroup"), data="cmd_clgroup")],
            BACK_ROW,
        )
    ),
    "help_promote": (
        f"👮 **{frak('Admin Management')}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [success(frak("/promote"), data="cmd_promote"),
             danger(frak("/demote"), data="cmd_demote")],
            [primary(frak("/title <text>"), data="cmd_title"),
             primary(frak("/admins"), data="cmd_admins")],
            BACK_ROW,
        )
    ),
    "help_group": (
        f"🔒 **{frak('Group Protection')}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [danger(frak("/lock"), data="cmd_lock"),
             success(frak("/unlock"), data="cmd_unlock")],
            [primary(frak("/setgrouppic 10|20|30"), data="cmd_setgrouppic")],
            [primary(frak("/groupinfo"), data="cmd_groupinfo"),
             success(frak("/snapshotgroup"), data="cmd_snapshotgroup2")],
            BACK_ROW,
        )
    ),
    "help_info": (
        f"📊 **{frak('Info Commands')}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [primary(frak("/info [@user]"), data="cmd_info"),
             primary(frak("/id"), data="cmd_id")],
            [success(frak("/ping"), data="cmd_ping"),
             primary(frak("/help"), data="cmd_help2")],
            BACK_ROW,
        )
    ),
    "help_broadcast": (
        f"📢 **{frak('Broadcast')}** 👑 {frak('Owner Only')}\n\n"
        f"_{frak('In private chat, reply to any message with /broadcast')}_\n"
        f"_{frak('to send it to ALL groups the bot is in.')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        lambda: markup(
            [danger(frak("/broadcast  (reply to msg)"), data="cmd_broadcast")],
            BACK_ROW,
        )
    ),
}


def register(app: Client):

    @app.on_message(filters.command("start") & filters.private)
    async def cmd_start(client: Client, message: Message):
        uid = message.from_user.id
        is_owner = uid == OWNER_ID
        is_auth = is_authorized(uid)

        if not is_owner and not is_auth:
            return await message.reply(
                f"🔒 **{frak('Access Restricted')}**\n\n"
                f"{frak('You are not authorized.')}\n"
                f"**{frak('Owner command:')}** `/auth {uid}`"
                f"{MADARA}",
                reply_markup=markup([danger(frak("✦ Unauthorized ✦"))])
            )

        name = message.from_user.first_name or "User"
        sticker_id = await _get_random_sticker(client)
        if sticker_id:
            try:
                await client.send_sticker(message.chat.id, sticker_id)
            except Exception:
                pass

        await asyncio.sleep(0.7)
        anim = await message.reply(f"**{frak('HLO THERE')}** . . . . .")
        await asyncio.sleep(0.9)
        await anim.edit(
            f"**{frak('HLO THERE')}** . . . . .\n\n"
            f"⚡ **{frak('STARTING AURA PROTECTOR')}** . . ."
        )
        await asyncio.sleep(1.1)
        await anim.edit(
            f"**{frak('HLO THERE')}** . . . . .\n\n"
            f"⚡ **{frak('STARTING AURA PROTECTOR')}** . . .\n\n"
            f"🛡️ **{frak('ALL SYSTEMS LOADED')}** ✅"
        )
        await asyncio.sleep(0.9)
        try:
            await anim.delete()
        except Exception:
            pass

        me = await client.get_me()
        role_val = frak("Owner 👑") if is_owner else frak("Authorized User ✅")
        await client.send_message(
            message.chat.id,
            f"🤖 **{frak('GuardBot — Group Shield')}**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👋 {frak('Welcome back')}, **{name}**!\n"
            f"🎖️ {frak('Role')}: {role_val}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ **{frak('I am your Group Guardian')}**\n"
            f"_{frak('Notes · Rules · Filters · Anti-Flood · Protection')}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            reply_markup=markup(
                [
                    primary(frak("📋 Help & Commands"), data="help_main"),
                    success(frak("✦ Add to Group ✦"),
                            url=f"https://t.me/{me.username}?startgroup=true"),
                ],
                [
                    primary(frak("ℹ️ About"), data="show_info"),
                    danger(frak("📢 Broadcast"), data="help_broadcast"),
                ]
            )
        )

    @app.on_callback_query(filters.regex("^help_main$"))
    async def cb_help_main(client: Client, query: CallbackQuery):
        await query.answer()
        me = await client.get_me()
        await query.message.edit(
            f"📋 **{frak('GuardBot Commands')}**\n\n"
            f"_{frak('Tap a category to see its commands:')}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            reply_markup=_main_menu_kb(me.username)
        )

    @app.on_callback_query(filters.regex("^help_"))
    async def cb_help_category(client: Client, query: CallbackQuery):
        key = query.data
        if key not in CATEGORY_CONTENT:
            await query.answer()
            return
        await query.answer()
        text, kb_fn = CATEGORY_CONTENT[key]
        await query.message.edit(
            text + MADARA,
            reply_markup=kb_fn()
        )

    @app.on_callback_query(filters.regex("^cmd_"))
    async def cb_cmd_detail(client: Client, query: CallbackQuery):
        cmd_map = {
            "cmd_giveaura": f"/giveaura — {frak('Reply to user to certify them (makes them admin)')}",
            "cmd_removeaura": f"/removeaura — {frak('Reply to user to revoke certification')}",
            "cmd_certified": f"/certified — {frak('List all certified members in this group')}",
            "cmd_snapshotgroup": f"/snapshotgroup — {frak('Save current group name & photo as protected values')}",
            "cmd_approve": f"/approve — {frak('Reply to user to approve them (bypass filters)')}",
            "cmd_unapprove": f"/unapprove — {frak('Reply to user to remove their approval')}",
            "cmd_setwelcome": f"/setwelcome <text> — {frak('Set custom welcome message. Variables: {name} {first} {chat} {id}')}",
            "cmd_setwelcome_off": f"/setwelcome off — {frak('Disable welcome messages for this group')}",
            "cmd_welcome": f"/welcome — {frak('Check current welcome settings')}",
            "cmd_welcome_vars": f"{frak('Variables:')} {{name}} = {frak('mention')}, {{first}} = {frak('first name')}, {{chat}} = {frak('group name')}, {{id}} = {frak('user ID')}",
            "cmd_save": f"/save notename text — {frak('Save a note. Or reply to a message with /save notename')}",
            "cmd_get": f"/get notename — {frak('Retrieve a saved note')}",
            "cmd_notes": f"/notes — {frak('List all saved notes in this group')}",
            "cmd_clear": f"/clear notename — {frak('Delete a specific note')}",
            "cmd_clearall": f"/clearall — {frak('Delete ALL notes in this group')}",
            "cmd_hashtag": f"#notename — {frak('Just type #notename in chat to get it instantly')}",
            "cmd_setrules": f"/setrules <text> — {frak('Set group rules. Or reply to a message')}",
            "cmd_rules": f"/rules — {frak('Show group rules to everyone')}",
            "cmd_resetrules": f"/resetrules — {frak('Delete all group rules')}",
            "cmd_filter": f"/filter keyword response — {frak('Auto-reply when keyword is detected')}",
            "cmd_filters": f"/filters — {frak('List all active filters')}",
            "cmd_stop": f"/stop keyword — {frak('Remove a filter')}",
            "cmd_stopall": f"/stopall — {frak('Remove ALL filters')}",
            "cmd_setflood": f"/setflood 5 — {frak('Mute user after 5 messages in 5 seconds. Adjust number as needed')}",
            "cmd_flood": f"/flood — {frak('Check current anti-flood settings')}",
            "cmd_setflood_off": f"/setflood 0 — {frak('Disable anti-flood')}",
            "cmd_ban": f"/ban [reason] — {frak('Reply to user to permanently ban them')}",
            "cmd_unban": f"/unban — {frak('Reply to user to unban them')}",
            "cmd_tban": f"/tban 1h — {frak('Temp ban. Use: 1m, 1h, 1d, 1w')}",
            "cmd_kick": f"/kick — {frak('Reply to user to kick them (they can rejoin)')}",
            "cmd_mute": f"/mute — {frak('Reply to user to mute (no messages)')}",
            "cmd_unmute": f"/unmute — {frak('Reply to user to unmute')}",
            "cmd_tmute": f"/tmute 1h — {frak('Temp mute. Use: 1m, 1h, 1d')}",
            "cmd_warn": f"/warn [reason] — {frak('Warn user. 3 warnings = auto-ban')}",
            "cmd_unwarn": f"/unwarn — {frak('Remove last warning from user')}",
            "cmd_warns": f"/warns — {frak('Check how many warnings a user has')}",
            "cmd_resetwarns": f"/resetwarns — {frak('Reset all warnings for a user')}",
            "cmd_pin": f"/pin — {frak('Reply to message to pin it')}",
            "cmd_unpin": f"/unpin — {frak('Unpin the latest pinned message')}",
            "cmd_unpinall": f"/unpinall — {frak('Unpin ALL pinned messages')}",
            "cmd_del": f"/del — {frak('Reply to message to delete it')}",
            "cmd_purge": f"/purge — {frak('Delete all messages from reply to now')}",
            "cmd_clgroup": f"/clgroup — {frak('Delete ALL messages in the group (use with care!)')}",
            "cmd_promote": f"/promote — {frak('Reply to user to make them admin')}",
            "cmd_demote": f"/demote — {frak('Reply to user to remove their admin rights')}",
            "cmd_title": f"/title <text> — {frak('Set custom admin title for user')}",
            "cmd_admins": f"/admins — {frak('List all admins in this group')}",
            "cmd_lock": f"/lock — {frak('Lock group (only admins can send messages)')}",
            "cmd_unlock": f"/unlock — {frak('Unlock group')}",
            "cmd_setgrouppic": f"/setgrouppic 10|20|30 — {frak('Set media auto-delete timer in seconds')}",
            "cmd_groupinfo": f"/groupinfo — {frak('Show all protection settings for this group')}",
            "cmd_snapshotgroup2": f"/snapshotgroup — {frak('Save current group name & photo as protected values')}",
            "cmd_info": f"/info [@user] — {frak('Show user info (ID, name, status, warns)')}",
            "cmd_id": f"/id — {frak('Get your ID, or reply to get another user ID')}",
            "cmd_ping": f"/ping — {frak('Check bot response time (latency)')}",
            "cmd_help2": f"/help — {frak('Show this command menu')}",
            "cmd_broadcast": f"/broadcast — {frak('Owner only! In PM, reply to any message with this to send to all groups')}",
        }
        text = cmd_map.get(query.data, frak("Command info not found."))
        await query.answer(text[:200], show_alert=True)

    @app.on_callback_query(filters.regex("^show_info$"))
    async def cb_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.edit(
            f"ℹ️ **{frak('About GuardBot')}**\n\n"
            f"🤖 **{frak('Version:')}** 4.0\n"
            f"⚙️ **{frak('Framework:')}** Kurigram v2.2.23\n"
            f"🐍 **{frak('Language:')}** Python 3.11\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ **{frak('Active Protections:')}**\n"
            f"• ✅ {frak('Slang filter — all languages + bots')}\n"
            f"• ✅ {frak('Illegal media auto-removal')}\n"
            f"• ✅ {frak('Group name & photo shield (owner exempt)')}\n"
            f"• ✅ {frak('Certified member system')}\n"
            f"• ✅ {frak('Notes, Rules, Filters, Anti-Flood')}\n"
            f"• ✅ {frak('Welcome with spoiler profile photo')}\n"
            f"• ✅ {frak('Full MissRose-style admin suite')}\n"
            f"• ✅ {frak('Warn system (3 strikes = ban)')}\n"
            f"• ✅ {frak('Owner broadcast system')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            reply_markup=markup(
                [success(frak("← Back"), data="show_start"),
                 primary(frak("📋 Commands"), data="help_main")]
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
            f"_{frak('Notes · Rules · Filters · Anti-Flood · Protection')}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            reply_markup=markup(
                [
                    primary(frak("📋 Help & Commands"), data="help_main"),
                    success(frak("✦ Add to Group ✦"),
                            url=f"https://t.me/{me.username}?startgroup=true"),
                ],
                [
                    primary(frak("ℹ️ About"), data="show_info"),
                    danger(frak("📢 Broadcast"), data="help_broadcast"),
                ]
            )
        )

    @app.on_message(filters.command("help"))
    async def cmd_help(client: Client, message: Message):
        me = await client.get_me()
        await message.reply(
            f"📋 **{frak('GuardBot Commands')}**\n\n"
            f"_{frak('Tap a category to see its commands:')}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            reply_markup=_main_menu_kb(me.username)
        )

    @app.on_callback_query(filters.regex("^noop$"))
    async def cb_noop(client: Client, query: CallbackQuery):
        await query.answer()
