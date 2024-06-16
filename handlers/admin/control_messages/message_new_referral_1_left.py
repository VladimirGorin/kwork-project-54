from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from states import AdminState
from database import get_param, update_param
from utils import get_menu, variables_str
from handlers.admin.commons import back_menu

router = Router()
param_code = 'message_new_referral_1_left'
button_caption = 'Новый реферал, остался 1'


@router.message(ButtonFilter(button_caption))
async def handler(message: Message, state: FSMContext):
    text = f'<b>{button_caption}</b>\n\nТекущее сообщение:'
    await message.answer(text)

    current_message = await get_param(param_code)

    await message.answer(text=current_message)

    text = (f'Отправьте новое сообщение или нажмите кнопку Назад.\n\n'
            f'Вы можете использовать переменные:\n{variables_str}')
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)
    await state.set_state(AdminState.WaitingNewReferal1LeftMessage)


@router.message(StateFilter(AdminState.WaitingNewReferal1LeftMessage))
async def handler(message: Message):
    text = message.html_text
    menu = get_menu(back_menu)
    await update_param(param_code, text)

    text = f'<b>{button_caption}</b>\n\nТекущее сообщение:'
    await message.answer(text)

    text = await get_param(param_code)
    await message.answer(text=text)

    text = f'<b>{button_caption}</b>\n\nCообщение обновлено!'
    await message.answer(text, reply_markup=menu)
