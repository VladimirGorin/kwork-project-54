from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from states import AdminState
from utils import get_menu, sending, variables_str, get_text_with_variables
from .commons import back_menu, main_menu
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from database import create_job
from my_types import User

router = Router()


@router.message(ButtonFilter('⚡️ Моментальная рассылка'))
async def handler(message: Message, state: FSMContext):
    await state.set_state(AdminState.WaitingSendingMessage)
    text = ('Отправьте сообщение, которое необходимо разослать пользователям бота.\n\n'
            f'Вы можете использовать переменные:\n{variables_str}')
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)


@router.message(ButtonFilter('⌛️ Отложенная рассылка'))
async def handler(message: Message, state: FSMContext):
    await state.set_state(AdminState.WaitingSendingDatetime)
    now = datetime.now().strftime('%H:%M %d.%m.%Y')
    text = f'Укажите дату и время запуска рассылки.\nТекущая дата и время: <code>{now}</code>'
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)


@router.message(StateFilter(AdminState.WaitingSendingDatetime))
async def handler(message: Message, state: FSMContext):
    try:
        moment = datetime.strptime(message.text, '%H:%M %d.%m.%Y')
        await state.update_data({'moment': moment})
        await state.set_state(AdminState.WaitingSendingMessage)
        text = ('Отправьте сообщение, которое необходимо разослать пользователям бота.\n\n'
                f'Вы можете использовать переменные:\n{variables_str}')
    except:
        now = datetime.now().strftime('%H:%M %d.%m.%Y')
        text = f'Укажите дату и время запуска рассылки.\nТекущая дата и время: <code>{now}</code>'
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)


@router.message(StateFilter(AdminState.WaitingSendingMessage))
async def handler(message: Message, state: FSMContext, user: User):
    data = await state.get_data()
    start = data.get('moment', datetime.now() + timedelta(seconds=5))
    text = message.html_text
    if message.photo:
        photo = message.photo[-1].file_id
    else:
        photo = None
    job_id = await create_job('instant_sending', start, text, photo, user.user_id)
    text = (f'Создана задача №{job_id} на отправку данного сообщения пользователям бота.\n'
            f'Запуск задачи в {start.strftime("%H:%M %d.%m.%Y")}\n'
            'По завершению вы получите отчет о рассылке.')
    menu = get_menu(main_menu)
    await message.reply(text, reply_markup=menu)
    await state.set_state(AdminState.Default)
