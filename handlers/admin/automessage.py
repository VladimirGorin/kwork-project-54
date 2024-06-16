from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters import ButtonFilter, StateFilter
from .commons import back_menu
from database import get_automessages, create_automessage, get_automessage, delete_automessage, recovery_automessage
from utils import get_menu, get_delay_str, get_delay_int, get_inline
from states import AdminState
from callback_factory import Automessage


router = Router()

automessage_menu = ['Добавить автосообщение', *back_menu]

anchors = {
    '{username}': 'Юзернэйм пользователя',
    '{first_name}': 'Имя пользователя',
    '{last_name}': 'Фамилия пользователя',
    '{invite_url}': 'Пригласительная ссылка',
    '{quantity_refers}': 'Текущее количество рефералов',
    '{needed_refers}': 'Необходимое количество рефералов',
    '{remain_refers}': 'Осталось пригласить рефералов'
}


@router.message(ButtonFilter('🤖 Автосообщения'))
async def handler(message: Message):
    text = 'Управление автосообщениями:'
    menu = get_menu(automessage_menu)
    await message.answer(text=text, reply_markup=menu)
    automessages = await get_automessages()
    for automessage_id, text, photo, delay_int in automessages:
        delay_str = get_delay_str(delay_int)
        text = f'Задержка: {delay_str}\n\n{text}'
        inline = get_inline([('❌ Удалить', Automessage(action='delete', value=automessage_id))])
        if photo:
            await message.answer_photo(caption=text,
                                       photo=photo,
                                       reply_markup=inline)
        else:
            await message.answer(text=text,
                                 reply_markup=inline)


@router.message(ButtonFilter('Добавить автосообщение'))
async def handler(message: Message, state: FSMContext):
    text = ('Укажите задержку перед отправкой автосообщения.\n'
            'Формат - <code>3д 12ч 10м 15с</code>')
    menu = get_menu(back_menu)
    await state.set_state(AdminState.WaitingAutomessageDelay)
    await message.answer(text=text,
                         reply_markup=menu)


@router.message(StateFilter(AdminState.WaitingAutomessageDelay))
async def handler(message: Message, state: FSMContext):
    try:
        delay_int = get_delay_int(message.text)
        await state.set_state(AdminState.WaitingAutomessage)
        await state.update_data({'delay_int': delay_int, 'delay_str': message.text})
        anchors_str = '\n'.join([f'<code>{key}</code> - {value}' for key, value in anchors.items()])
        text = ('Отправьте автосообщение, которое будет использовано в качестве автосообщения.\n\n'
                f'Вы можете использовать переменные: \n{anchors_str}')
    except:
        text = 'Не удалось распознать задержку, проверьте вводимый формат!'
    menu = get_menu(back_menu)
    await message.answer(text, reply_markup=menu)


@router.message(StateFilter(AdminState.WaitingAutomessage))
async def handler(message: Message, state: FSMContext):
    message_text = message.html_text
    if message.photo:
        photo = message.photo[-1].file_id
    else:
        photo = None
    data = await state.get_data()
    delay_int = data.get('delay_int')
    delay_str = data.get('delay_str')
    await create_automessage(message_text, photo, delay_int)

    text = 'Автосообщение успешно добавлено!'
    menu = get_menu(automessage_menu)
    await message.answer(text, reply_markup=menu)

    text = f'Задержка: {delay_str}\n\n{message_text}'
    if photo:
        await message.answer_photo(caption=text,
                                   photo=photo)
    else:
        await message.answer(text=text)

    await state.set_state(AdminState.Default)
    await state.set_data({})


@router.callback_query(Automessage.filter(F.action == 'delete'))
async def handler(callback_query: CallbackQuery, callback_data: Automessage):
    automessage_id = callback_data.value
    await delete_automessage(automessage_id)
    inline = get_inline([('✅ Восстановить', Automessage(action='recovery', value=automessage_id))])
    await callback_query.message.edit_reply_markup(reply_markup=inline)


@router.callback_query(Automessage.filter(F.action == 'recovery'))
async def handler(callback_query: CallbackQuery, callback_data: Automessage):
    automessage_id = callback_data.value
    await recovery_automessage(automessage_id)
    inline = get_inline([('❌ Удалить', Automessage(action='delete', value=automessage_id))])
    await callback_query.message.edit_reply_markup(reply_markup=inline)
