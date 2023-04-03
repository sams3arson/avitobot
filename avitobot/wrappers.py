from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from avitobot.states import State
from avitobot.custom_types import UserId
from typing import Callable
import re

def filter_state_wrapper(state: State, user_states: dict[UserId, State]) -> \
        Callable[[filters.Filter, Client, Message], bool]:
    """Filter wrapper for Pyrogram handler of messages. Pass state 
    from states.State as argument and it will return True if the user is in 
    that state."""
    def filter_inner(filt: filters.Filter, client: Client, update: Message):
        if user_states.get(update.from_user.id) == state:
            return True
        return False
    return filter_inner
