from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from states import AdminState
from database import get_param, update_param
from utils import get_menu, variables_str
from handlers.admin.commons import back_menu

router = Router()
param_code_message = 'message_start'
param_code_image = 'image_start'
button_caption = 'Стартовое сообщение'


@router.message(ButtonFilter(button_caption))
async def handler(message: Message, state: FSMContext):
    text = f'<b>{button_caption}</b>\n\nТекущее сообщение:'
    await message.answer(text)

    current_message = await get_param(param_code_message)
    current_image = await get_param(param_code_image)

    try:
        await message.answer_photo(caption=current_message,
                                   photo=current_image)
    except:
        await message.answer(text=current_message)

    text = (f'Отправьте новое сообщение или нажмите кнопку Назад.\n\n'
            f'Вы можете использовать переменные:\n{variables_str}')
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)
    await state.set_state(AdminState.WaitingStartMessage)


@router.message(StateFilter(AdminState.WaitingStartMessage))
async def handler(message: Message):
    menu = get_menu(back_menu)
    if message.photo:
        photo = message.photo[-1].file_id
    else:
        photo = None
    text = message.html_text

    await update_param(param_code_message, text)
    await update_param(param_code_image, photo)

    text = f'<b>{button_caption}</b>\n\nCообщение обновлено!'
    await message.answer(text)

    text = await get_param(param_code_message)
    image = await get_param(param_code_image)

    try:
        await message.answer_photo(caption=text,
                                   photo=image)
    except:
        await message.answer(text=text)

    text = (f'Отправьте новое сообщение или нажмите кнопку Назад.\n\n'
            f'Вы можете использовать переменные:\n{variables_str}')
    await message.answer(text, reply_markup=menu)
