from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle


def btn(text: str, data: str = None, url: str = None,
        style: ButtonStyle = ButtonStyle.DEFAULT) -> InlineKeyboardButton:
    if url:
        return InlineKeyboardButton(text=text, url=url, style=style)
    return InlineKeyboardButton(text=text, callback_data=data or "noop", style=style)


def primary(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
    return btn(text, data=data, url=url, style=ButtonStyle.PRIMARY)


def success(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
    return btn(text, data=data, url=url, style=ButtonStyle.SUCCESS)


def danger(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
    return btn(text, data=data, url=url, style=ButtonStyle.DANGER)


def default(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
    return btn(text, data=data, url=url, style=ButtonStyle.DEFAULT)


def markup(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(list(rows))
