from aiogram.filters import BaseFilter
from aiogram.types import Message
from database import get_user
from aiogram.filters import Command, StateFilter

CommandFilter = Command


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await get_user(message.from_user.id)
        return user.is_admin


class ButtonFilter(BaseFilter):
    def __init__(self, button_caption: str):
        self.button_caption = button_caption

    async def __call__(self, message: Message) -> bool:
        return self.button_caption == message.text
