import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ParseMode

from config import OWNER_ID
from database import is_authorized
from utils.font import frak
from utils.buttons import markup, primary, success, danger
from utils.emojis import em, ems, em_row

STICKER_SET = "guri20_by_fStikBot"
_sticker_cache = []
MADARA = f"\n\n— <b>{frak('Powered by Madara')}</b> 🔥"
PM = ParseMode.HTML


async def _get_random_sticker(client):
    global _sticker_cache
    if not _sticker_cache:
        try:
            ss = await client.get_sticker_set(STICKER_SET)
            _sticker_cache = [s.file_id for s in ss.stickers]
        except Exception:
            return None
    return random.choice(_sticker_cache) if _sticker_cache else None


def _main_menu_kb(me_username):
    return markup(
        [success(frak("⭐ Certification"),    data="help_certified"),
         primary(frak("👋 Welcome"),           data="help_welcome")],
        [primary(frak("📝 Notes"),             data="help_notes"),
         success(frak("📜 Rules"),             data="help_rules")],
        [primary(frak("🔍 Filters"),           data="help_filters"),
         danger( frak("🌊 Anti-Flood"),        data="help_flood")],
        [danger( frak("🔨 Ban / Kick"),        data="help_ban"),
         danger( frak("🔇 Mute"),              data="help_mute")],
        [danger( frak("⚠️ Warns"),             data="help_warns"),
         primary(frak("📌 Messages"),          data="help_messages")],
        [success(frak("👮 Promote / Demote"),  data="help_promote"),
         primary(frak("🔒 Group"),             data="help_group")],
        [primary(frak("📊 Info / Ping"),       data="help_info"),
         danger( frak("📢 Broadcast"),         data="help_broadcast")],
        [success(frak("✦ Add to Group ✦"),
                 url=f"https://t.me/{me_username}?startgroup=true")],
    )


BACK_ROW = [danger(frak("← Back"), data="help_main")]

CATEGORY_CONTENT = {
    "help_certified": (
        lambda: (
            f"{em_row(5)}\n"
            f"⭐ <b>{frak('Certification Commands')}</b>\n\n"
            f"{em()} <i>{frak('Certified members bypass all filters and get admin rights.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/giveaura"),     data="cmd_giveaura"),
                 success(frak("/removeaura"),   data="cmd_removeaura")],
                [primary(frak("/certified"),    data="cmd_certified"),
                 primary(frak("/snapshotgroup"),data="cmd_snapshotgroup")],
                [success(frak("/approve"),      data="cmd_approve"),
                 danger( frak("/unapprove"),    data="cmd_unapprove")],
                BACK_ROW,
            )
        )
    ),
    "help_welcome": (
        lambda: (
            f"{em_row(5)}\n"
            f"👋 <b>{frak('Welcome System')}</b>\n\n"
            f"{em()} <i>{frak('Auto-welcome new members with spoiler profile photo.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/setwelcome <text>"), data="cmd_setwelcome")],
                [danger( frak("/setwelcome off"),    data="cmd_setwelcome_off")],
                [primary(frak("/welcome"),           data="cmd_welcome")],
                [primary(frak("{name}  {first}  {chat}  {id}"), data="cmd_welcome_vars")],
                BACK_ROW,
            )
        )
    ),
    "help_notes": (
        lambda: (
            f"{em_row(5)}\n"
            f"📝 <b>{frak('Notes System')}</b>\n\n"
            f"{em()} <i>{frak('Save and retrieve notes. Type #notename to get a note instantly.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/save name text"), data="cmd_save"),
                 primary(frak("/get name"),       data="cmd_get")],
                [success(frak("/notes"),          data="cmd_notes"),
                 danger( frak("/clear name"),     data="cmd_clear")],
                [danger( frak("/clearall"),       data="cmd_clearall"),
                 primary(frak("#notename"),       data="cmd_hashtag")],
                BACK_ROW,
            )
        )
    ),
    "help_rules": (
        lambda: (
            f"{em_row(5)}\n"
            f"📜 <b>{frak('Rules System')}</b>\n\n"
            f"{em()} <i>{frak('Set and display group rules.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/setrules <text>"), data="cmd_setrules")],
                [primary(frak("/rules"),           data="cmd_rules"),
                 danger( frak("/resetrules"),      data="cmd_resetrules")],
                BACK_ROW,
            )
        )
    ),
    "help_filters": (
        lambda: (
            f"{em_row(5)}\n"
            f"🔍 <b>{frak('Auto Filter System')}</b>\n\n"
            f"{em()} <i>{frak('Auto-reply when keywords are detected in messages.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/filter keyword reply"), data="cmd_filter")],
                [primary(frak("/filters"),             data="cmd_filters"),
                 danger( frak("/stop keyword"),        data="cmd_stop")],
                [danger( frak("/stopall"),             data="cmd_stopall")],
                BACK_ROW,
            )
        )
    ),
    "help_flood": (
        lambda: (
            f"{em_row(5)}\n"
            f"🌊 <b>{frak('Anti-Flood System')}</b>\n\n"
            f"{em()} <i>{frak('Auto-mute users who send too many messages too fast.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/setflood <num>"),       data="cmd_setflood")],
                [primary(frak("/flood"),                data="cmd_flood"),
                 danger( frak("/setflood 0  (off)"),    data="cmd_setflood_off")],
                BACK_ROW,
            )
        )
    ),
    "help_ban": (
        lambda: (
            f"{em_row(5)}\n"
            f"🔨 <b>{frak('Ban & Kick Commands')}</b>\n\n"
            f"{em()} <i>{frak('Reply to a user message to target them.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [danger( frak("/ban"),          data="cmd_ban"),
                 success(frak("/unban"),        data="cmd_unban")],
                [danger( frak("/tban <1h/2d>"), data="cmd_tban"),
                 danger( frak("/kick"),         data="cmd_kick")],
                BACK_ROW,
            )
        )
    ),
    "help_mute": (
        lambda: (
            f"{em_row(5)}\n"
            f"🔇 <b>{frak('Mute Commands')}</b>\n\n"
            f"{em()} <i>{frak('Reply to a user message to target them.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [danger( frak("/mute"),          data="cmd_mute"),
                 success(frak("/unmute"),        data="cmd_unmute")],
                [danger( frak("/tmute <1h/2d>"), data="cmd_tmute")],
                BACK_ROW,
            )
        )
    ),
    "help_warns": (
        lambda: (
            f"{em_row(5)}\n"
            f"⚠️ <b>{frak('Warn System')}</b>\n\n"
            f"{em()} <i>{frak('3 warnings = auto-ban. Reply to target user.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [danger( frak("/warn [reason]"), data="cmd_warn"),
                 success(frak("/unwarn"),        data="cmd_unwarn")],
                [primary(frak("/warns"),         data="cmd_warns"),
                 danger( frak("/resetwarns"),    data="cmd_resetwarns")],
                BACK_ROW,
            )
        )
    ),
    "help_messages": (
        lambda: (
            f"{em_row(5)}\n"
            f"📌 <b>{frak('Message Commands')}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/pin"),      data="cmd_pin"),
                 danger( frak("/unpin"),    data="cmd_unpin")],
                [danger( frak("/unpinall"), data="cmd_unpinall"),
                 danger( frak("/del"),      data="cmd_del")],
                [danger( frak("/purge"),    data="cmd_purge"),
                 danger( frak("/clgroup"), data="cmd_clgroup")],
                BACK_ROW,
            )
        )
    ),
    "help_promote": (
        lambda: (
            f"{em_row(5)}\n"
            f"👮 <b>{frak('Admin Management')}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [success(frak("/promote"),     data="cmd_promote"),
                 danger( frak("/demote"),      data="cmd_demote")],
                [primary(frak("/title <text>"),data="cmd_title"),
                 primary(frak("/admins"),      data="cmd_admins")],
                BACK_ROW,
            )
        )
    ),
    "help_group": (
        lambda: (
            f"{em_row(5)}\n"
            f"🔒 <b>{frak('Group Protection')}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [danger( frak("/lock"),                  data="cmd_lock"),
                 success(frak("/unlock"),                data="cmd_unlock")],
                [primary(frak("/setgrouppic 10|20|30"),  data="cmd_setgrouppic")],
                [primary(frak("/groupinfo"),             data="cmd_groupinfo"),
                 success(frak("/snapshotgroup"),         data="cmd_snapshotgroup2")],
                BACK_ROW,
            )
        )
    ),
    "help_info": (
        lambda: (
            f"{em_row(5)}\n"
            f"📊 <b>{frak('Info Commands')}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [primary(frak("/info [@user]"), data="cmd_info"),
                 primary(frak("/id"),           data="cmd_id")],
                [success(frak("/ping"),         data="cmd_ping"),
                 primary(frak("/help"),         data="cmd_help2")],
                BACK_ROW,
            )
        )
    ),
    "help_broadcast": (
        lambda: (
            f"{em_row(5)}\n"
            f"📢 <b>{frak('Broadcast')}</b> 👑 {frak('Owner Only')}\n\n"
            f"{em()} <i>{frak('In private chat, reply to any message with /broadcast to send to ALL groups.')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            markup(
                [danger(frak("/broadcast  (reply to msg)"), data="cmd_broadcast")],
                BACK_ROW,
            )
        )
    ),
}

CMD_MAP = {
    "cmd_giveaura":       "/giveaura — Reply to user to certify them (makes them admin)",
    "cmd_removeaura":     "/removeaura — Reply to user to revoke certification",
    "cmd_certified":      "/certified — List all certified members in this group",
    "cmd_snapshotgroup":  "/snapshotgroup — Save current group name & photo as protected values",
    "cmd_approve":        "/approve — Reply to user to approve them (bypass filters)",
    "cmd_unapprove":      "/unapprove — Reply to user to remove their approval",
    "cmd_setwelcome":     "/setwelcome <text> — Set custom welcome. Variables: {name} {first} {chat} {id}",
    "cmd_setwelcome_off": "/setwelcome off — Disable welcome messages for this group",
    "cmd_welcome":        "/welcome — Check current welcome settings",
    "cmd_welcome_vars":   "Variables: {name}=mention, {first}=first name, {chat}=group, {id}=user ID",
    "cmd_save":           "/save notename text — Save a note. Or reply to a msg with /save notename",
    "cmd_get":            "/get notename — Retrieve a saved note",
    "cmd_notes":          "/notes — List all saved notes in this group",
    "cmd_clear":          "/clear notename — Delete a specific note",
    "cmd_clearall":       "/clearall — Delete ALL notes in this group",
    "cmd_hashtag":        "#notename — Type #notename in chat to get it instantly",
    "cmd_setrules":       "/setrules <text> — Set group rules. Or reply to a message",
    "cmd_rules":          "/rules — Show group rules to everyone",
    "cmd_resetrules":     "/resetrules — Delete all group rules",
    "cmd_filter":         "/filter keyword response — Auto-reply when keyword is detected",
    "cmd_filters":        "/filters — List all active filters",
    "cmd_stop":           "/stop keyword — Remove a filter",
    "cmd_stopall":        "/stopall — Remove ALL filters",
    "cmd_setflood":       "/setflood 5 — Mute after 5 messages in 5 seconds",
    "cmd_flood":          "/flood — Check current anti-flood settings",
    "cmd_setflood_off":   "/setflood 0 — Disable anti-flood",
    "cmd_ban":            "/ban [reason] — Reply to user to permanently ban",
    "cmd_unban":          "/unban — Reply to user to unban",
    "cmd_tban":           "/tban 1h — Temp ban. Use: 1m, 1h, 1d, 1w",
    "cmd_kick":           "/kick — Reply to user to kick (can rejoin)",
    "cmd_mute":           "/mute — Reply to user to mute (no messages)",
    "cmd_unmute":         "/unmute — Reply to user to unmute",
    "cmd_tmute":          "/tmute 1h — Temp mute. Use: 1m, 1h, 1d",
    "cmd_warn":           "/warn [reason] — Warn user. 3 warnings = auto-ban",
    "cmd_unwarn":         "/unwarn — Remove last warning from user",
    "cmd_warns":          "/warns — Check how many warnings a user has",
    "cmd_resetwarns":     "/resetwarns — Reset all warnings for a user",
    "cmd_pin":            "/pin — Reply to message to pin it",
    "cmd_unpin":          "/unpin — Unpin the latest pinned message",
    "cmd_unpinall":       "/unpinall — Unpin ALL pinned messages",
    "cmd_del":            "/del — Reply to message to delete it",
    "cmd_purge":          "/purge — Delete all messages from reply to now",
    "cmd_clgroup":        "/clgroup — Delete ALL messages in the group (use with care!)",
    "cmd_promote":        "/promote — Reply to user to make them admin",
    "cmd_demote":         "/demote — Reply to user to remove admin rights",
    "cmd_title":          "/title <text> — Set custom admin title for user",
    "cmd_admins":         "/admins — List all admins in this group",
    "cmd_lock":           "/lock — Lock group (only admins can send)",
    "cmd_unlock":         "/unlock — Unlock group",
    "cmd_setgrouppic":    "/setgrouppic 10|20|30 — Set media auto-delete timer in seconds",
    "cmd_groupinfo":      "/groupinfo — Show all protection settings for this group",
    "cmd_snapshotgroup2": "/snapshotgroup — Save current group name & photo as protected values",
    "cmd_info":           "/info [@user] — Show user info (ID, name, status, warns)",
    "cmd_id":             "/id — Get your ID, or reply to get another user ID",
    "cmd_ping":           "/ping — Check bot response time (latency)",
    "cmd_help2":          "/help — Show this command menu",
    "cmd_broadcast":      "/broadcast — Owner only! In PM, reply to any message to send to all groups",
}


def register(app: Client):

    @app.on_message(filters.command("start") & filters.private)
    async def cmd_start(client: Client, message: Message):
        uid = message.from_user.id
        is_owner = uid == OWNER_ID
        is_auth = is_authorized(uid)

        if not is_owner and not is_auth:
            return await message.reply(
                f"🔒 <b>{frak('Access Restricted')}</b>\n\n"
                f"{em()} {frak('You are not authorized.')}\n"
                f"{em()} <b>{frak('Owner command:')}</b> <code>/auth {uid}</code>"
                f"{MADARA}",
                parse_mode=PM,
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
        anim = await message.reply(
            f"<b>{frak('HLO THERE')}</b> . . . . .",
            parse_mode=PM
        )
        await asyncio.sleep(0.9)
        await anim.edit(
            f"<b>{frak('HLO THERE')}</b> . . . . .\n\n"
            f"⚡ <b>{frak('STARTING AURA PROTECTOR')}</b> . . .",
            parse_mode=PM
        )
        await asyncio.sleep(1.1)
        await anim.edit(
            f"<b>{frak('HLO THERE')}</b> . . . . .\n\n"
            f"⚡ <b>{frak('STARTING AURA PROTECTOR')}</b> . . .\n\n"
            f"🛡️ <b>{frak('ALL SYSTEMS LOADED')}</b> ✅",
            parse_mode=PM
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
            f"{em_row(6)}\n\n"
            f"🤖 <b>{frak('GuardBot — Group Shield')}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{em()} {frak('Welcome back')}, <b>{name}</b>!\n"
            f"{em()} {frak('Role')}: {role_val}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ <b>{frak('I am your Group Guardian')}</b>\n"
            f"{em()} <i>{frak('Notes · Rules · Filters · Anti-Flood · Protection')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{em_row(6)}"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=markup(
                [primary(frak("📋 Help & Commands"), data="help_main"),
                 success(frak("✦ Add to Group ✦"),
                         url=f"https://t.me/{me.username}?startgroup=true")],
                [primary(frak("ℹ️ About"),           data="show_info"),
                 danger( frak("📢 Broadcast"),       data="help_broadcast")]
            )
        )

    @app.on_callback_query(filters.regex("^help_main$"))
    async def cb_help_main(client: Client, query: CallbackQuery):
        await query.answer()
        me = await client.get_me()
        await query.message.edit(
            f"{em_row(5)}\n\n"
            f"📋 <b>{frak('GuardBot Commands')}</b>\n\n"
            f"{em()} <i>{frak('Tap a category to see its commands:')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=_main_menu_kb(me.username)
        )

    @app.on_callback_query(filters.regex("^help_"))
    async def cb_help_category(client: Client, query: CallbackQuery):
        key = query.data
        if key not in CATEGORY_CONTENT:
            return await query.answer()
        await query.answer()
        text, kb = CATEGORY_CONTENT[key]()
        await query.message.edit(
            text + MADARA,
            parse_mode=PM,
            reply_markup=kb
        )

    @app.on_callback_query(filters.regex("^cmd_"))
    async def cb_cmd_detail(client: Client, query: CallbackQuery):
        info = CMD_MAP.get(query.data, "Command info not found.")
        await query.answer(info[:200], show_alert=True)

    @app.on_callback_query(filters.regex("^show_info$"))
    async def cb_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.edit(
            f"{em_row(5)}\n\n"
            f"ℹ️ <b>{frak('About GuardBot')}</b>\n\n"
            f"{em()} <b>{frak('Version:')}</b> 4.0\n"
            f"{em()} <b>{frak('Framework:')}</b> Kurigram v2.2.23\n"
            f"{em()} <b>{frak('Language:')}</b> Python 3.11\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ <b>{frak('Active Protections:')}</b>\n"
            f"{em()} {frak('Slang filter — all languages + bots')}\n"
            f"{em()} {frak('Illegal media auto-removal')}\n"
            f"{em()} {frak('Group name & photo shield')}\n"
            f"{em()} {frak('Certified member system')}\n"
            f"{em()} {frak('Notes, Rules, Filters, Anti-Flood')}\n"
            f"{em()} {frak('Welcome with spoiler profile photo')}\n"
            f"{em()} {frak('Full MissRose-style admin suite')}\n"
            f"{em()} {frak('Warn system — 3 strikes = ban')}\n"
            f"{em()} {frak('Owner broadcast system')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{em_row(5)}"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=markup(
                [success(frak("← Back"),       data="show_start"),
                 primary(frak("📋 Commands"),  data="help_main")]
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
            f"{em_row(6)}\n\n"
            f"🤖 <b>{frak('GuardBot — Group Shield')}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{em()} {frak('Welcome back')}, <b>{name}</b>!\n"
            f"{em()} {frak('Role')}: {role_val}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ <b>{frak('I am your Group Guardian')}</b>\n"
            f"{em()} <i>{frak('Notes · Rules · Filters · Anti-Flood · Protection')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{em_row(6)}"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=markup(
                [primary(frak("📋 Help & Commands"), data="help_main"),
                 success(frak("✦ Add to Group ✦"),
                         url=f"https://t.me/{me.username}?startgroup=true")],
                [primary(frak("ℹ️ About"),           data="show_info"),
                 danger( frak("📢 Broadcast"),       data="help_broadcast")]
            )
        )

    @app.on_message(filters.command("help"))
    async def cmd_help(client: Client, message: Message):
        me = await client.get_me()
        await message.reply(
            f"{em_row(5)}\n\n"
            f"📋 <b>{frak('GuardBot Commands')}</b>\n\n"
            f"{em()} <i>{frak('Tap a category to see its commands:')}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{MADARA}",
            parse_mode=PM,
            reply_markup=_main_menu_kb(me.username)
        )

    @app.on_callback_query(filters.regex("^noop$"))
    async def cb_noop(client: Client, query: CallbackQuery):
        await query.answer()
