from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from filters import ButtonFilter
from database import get_users, get_param
from utils import get_inline
from callback_factory import Subscribers
from datetime import datetime

router = Router()
param_code_message = 'subscribers'


@router.message(ButtonFilter('👥 Подписчики'))
async def handler(message: Message):
    users = await get_users()
    needed_count_refers = await get_param('needed_number_of_referrals')
    count_total = len(users)
    count_get_gift = 0
    count_blocked = 0
    count_today = 0
    today = datetime.now().strftime('%Y-%m-%d')
    for user_id, username, first_name, last_name, blocked, inviter_id, count_refers, is_admin, created in users:
        if count_refers >= needed_count_refers:
            count_get_gift += 1
        if blocked:
            count_blocked += 1
        if today in created:
            count_today += 1
    text = (f"Всего пользователей: {count_total}\n"
            f"За сегодня: {count_today}\n"
            f'Активных пользователей: {count_total - count_blocked}\n'
            f"Заблокировали бота: {count_blocked}\n"
            f"Получили подарок: {count_get_gift}\n")
    inline = get_inline([('Список пользователей', Subscribers(action='show'))])
    await message.answer(text=text,
                         reply_markup=inline)


@router.callback_query(Subscribers.filter(F.action == 'show'))
async def handler(callback_query: CallbackQuery):
    await callback_query.answer()
    users = await get_users(blocked=0)
    users = [f"{index} ) " + (f'@{user[1]}' if user[1] else f"Пользователь") + f" ({user[0]})\n"
             for index, user in enumerate(users, start=1)]
    text = ''
    for index, user in enumerate(users):
        if len(text) + len(user) >= 4096:
            await callback_query.message.answer(text)
            text = user
        elif index == len(users) - 1:
            text += user
            await callback_query.message.answer(text)
        else:
            text += user
