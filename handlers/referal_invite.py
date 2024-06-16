from aiogram import Router
from aiogram.types import Message
from database import get_param
from logging import getLogger
from filters import ButtonFilter
from utils import get_text_with_variables
from my_types import User

router = Router()
logger = getLogger('handler_referal_invite')


@router.message(ButtonFilter('🔗 Реферальная ссылка'))
async def handler(message: Message, user: User):
    text = await get_param('message_invite_url')
    text = await get_text_with_variables(text=text,
                                         user_id=user.user_id)
    await message.answer(text=text)


