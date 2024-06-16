from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from states import AdminState
from database import get_param, update_param
from utils import get_menu
from .commons import back_menu

router = Router()
param_code = 'needed_number_of_referrals'


@router.message(ButtonFilter('🔢 Количество рефералов'))
async def handler(message: Message, state: FSMContext):
    current_value = await get_param(param_code)
    text = (f'<b>{message.text}</b>\n\n'
            f'Текущее значение: {current_value}\n\n'
            f'Введите новое значение или нажмите кнопку Назад:')
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)
    await state.set_state(AdminState.WaitingNumberReferals)


@router.message(StateFilter(AdminState.WaitingNumberReferals))
async def handler(message: Message):
    value = message.text
    menu = get_menu(back_menu)
    if value.isdigit():
        await update_param(param_code, value)
        text = (f'<b>Количество рефералов</b>\n\n'
                f'Текущее значение: {value}\n\n'
                f'Введите новое значение или нажмите кнопку Назад:')
    else:
        text = "Ошибка ввода - ожидалось число."
    await message.answer(text, reply_markup=menu)
