from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import CommandFilter, ButtonFilter, StateFilter
from states import AdminState
from utils import get_menu
from .commons import logger, main_menu


router = Router()


@router.message(CommandFilter('admin'))
@router.message(ButtonFilter('🔙 Назад'))
@router.message(ButtonFilter('⚙️ Админ панель'))
async def handler(message: Message, state: FSMContext):
    text = 'Выберите параметр для просмотра и изменения:'
    menu = get_menu(main_menu)
    await message.answer(text, reply_markup=menu)
    await state.set_state(AdminState.Default)
    await state.set_data({})




