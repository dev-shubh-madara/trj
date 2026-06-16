"""
Premium emoji utility — fetches custom emoji IDs from Telegram emoji packs
and provides helpers to embed them in HTML-mode messages.

Usage:
    from utils.emojis import em, ems, em_row, load_emoji_packs

    # In main.py startup:
    await load_emoji_packs(client)

    # In messages (use parse_mode=ParseMode.HTML):
    text = f"{em()} <b>Hello!</b> {em_row(3)}"
"""

import random
import logging

log = logging.getLogger("GuardBot.emojis")

PACKS = [
    "nfticecollection_by_EmojiRu_Bot",
    "blueeemojik",
]

_EMOJI_POOL: list[dict] = []

_PLAIN_FALLBACKS = [
    "🌟", "🔥", "💎", "✨", "🎯", "🛡️", "⚡", "🎉", "💫", "🌈",
    "🚀", "👑", "🎪", "🌊", "⭐", "🔮", "🎭", "🦋", "🌺", "🏆",
    "💥", "🌙", "🎶", "🍀", "🦄", "🌸", "🎊", "🔑", "💠", "🌀",
]

_loaded = False


async def load_emoji_packs(client) -> int:
    """Fetch custom emoji IDs from both emoji packs. Call once at startup."""
    global _EMOJI_POOL, _loaded
    _EMOJI_POOL.clear()

    for pack_name in PACKS:
        try:
            ss = await client.get_stickers(pack_name)
            count = 0
            for sticker in ss:
                custom_id = getattr(sticker, "custom_emoji_id", None)
                fallback = getattr(sticker, "emoji", "🌟") or "🌟"
                if custom_id:
                    _EMOJI_POOL.append({"id": custom_id, "fallback": fallback})
                    count += 1
            log.info(f"Loaded {count} emojis from pack '{pack_name}'")
        except Exception as e:
            log.warning(f"Could not load pack '{pack_name}': {e}")

    _loaded = True
    log.info(f"Total emoji pool: {len(_EMOJI_POOL)} custom emojis")
    return len(_EMOJI_POOL)


def _pick() -> dict | None:
    if _EMOJI_POOL:
        return random.choice(_EMOJI_POOL)
    return None


def em() -> str:
    """One random premium emoji tag, falls back to plain emoji."""
    e = _pick()
    if e:
        return f'<emoji id="{e["id"]}">{e["fallback"]}</emoji>'
    return random.choice(_PLAIN_FALLBACKS)


def ems(n: int = 3, sep: str = " ") -> str:
    """n random emoji tags joined by sep."""
    return sep.join(em() for _ in range(n))


def em_row(n: int = 5) -> str:
    """Decorative row of n emojis."""
    return ems(n, " ")
