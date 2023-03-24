from typing import TypeAlias, NamedTuple
from pyrogram.types import InlineKeyboardButton

UserId: TypeAlias = int
MessageId: TypeAlias = int

class CachedMarkup(NamedTuple):
    buttons: list[list[InlineKeyboardButton]]
    msg_id: MessageId

