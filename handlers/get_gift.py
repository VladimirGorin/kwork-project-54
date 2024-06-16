from aiogram import Router, Bot
from aiogram.types import Message
from database import get_param
from logging import getLogger
from filters import ButtonFilter
from my_types import User
from utils import get_text_with_variables

router = Router()
logger = getLogger('handler_get_gift')


@router.message(ButtonFilter('🎁 Получить подарок'))
async def handler(message: Message, user: User):
    needed_refers = await get_param('needed_number_of_referrals')
    if user.current_refers >= needed_refers:
        param = 'message_get_gift_success'
    else:
        param = 'message_get_gift_fail'
    text = await get_param(param)
    text = await get_text_with_variables(text=text,
                                         user_id=user.user_id,
                                         needed_refers=needed_refers,
                                         current_refers=user.current_refers,
                                         remain_refers=needed_refers - user.current_refers)
    await message.answer(text=text)
