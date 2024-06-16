from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from states import AdminState
from utils import get_menu
from handlers.admin.commons import message_menu

router = Router()


@router.message(ButtonFilter('💬 Управление сообщениями'))
@router.message(ButtonFilter('🔙 Назад'),
                AdminState.WaitingStartMessage)
async def handler(message: Message, state: FSMContext):
    text = 'Выберите сообщение для редактирования для просмотра и изменения:'
    menu = get_menu(message_menu)
    await message.answer(text, reply_markup=menu)
    await state.set_state(AdminState.Default)
    await state.set_data({})



