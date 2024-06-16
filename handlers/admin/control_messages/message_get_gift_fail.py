from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from states import AdminState
from database import get_param, update_param
from utils import get_menu, variables_str
from handlers.admin.commons import back_menu

router = Router()
param_code_message = 'message_get_gift_fail'
button_caption = 'Получить подарок - мало рефералов'


@router.message(ButtonFilter(button_caption))
async def handler(message: Message, state: FSMContext):
    text = f'<b>{button_caption}</b>\n\nТекущее сообщение:'
    await message.answer(text)
    current_message = await get_param(param_code_message)
    await message.answer(text=current_message)
    text = (f'Отправьте новое сообщение или нажмите кнопку Назад.\n\n'
            f'Вы можете использовать переменные:\n{variables_str}')
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)
    await state.set_state(AdminState.WaitingGetGiftFailMessage)


@router.message(StateFilter(AdminState.WaitingGetGiftFailMessage))
async def handler(message: Message):
    menu = get_menu(back_menu)
    current_message = message.html_text
    await update_param(param_code_message, current_message)
    text = f'<b>{button_caption}</b>\n\nCообщение обновлено!'
    await message.answer(text)
    await message.answer(current_message)
    text = (f'Отправьте новое сообщение или нажмите кнопку Назад.\n\n'
            f'Вы можете использовать переменные:\n{variables_str}')
    await message.answer(text, reply_markup=menu)
