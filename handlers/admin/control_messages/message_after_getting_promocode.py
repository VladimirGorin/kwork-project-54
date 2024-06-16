from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from states import AdminState
from database import get_param, update_param
from utils import get_menu, variables_str
from handlers.admin.commons import back_menu

router = Router()
param_code = 'message_after_getting_promocode'
button_caption = 'После необходимого количества рефералов'


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
    await state.set_state(AdminState.WaitingAfterGettingPromocodeMessage)


@router.message(StateFilter(AdminState.WaitingAfterGettingPromocodeMessage))
async def handler(message: Message):
    text = message.html_text
    menu = get_menu(back_menu)
    await update_param(param_code, text)
    text = f'<b>{button_caption}</b>\n\nCообщение обновлено!'
    await message.answer(text)
    text = await get_param(param_code)
    await message.answer(text=text)
    text = (f'Отправьте новое сообщение или нажмите кнопку Назад.\n\n'
            f'Вы можете использовать переменные:\n{variables_str}')
    await message.answer(text, reply_markup=menu)