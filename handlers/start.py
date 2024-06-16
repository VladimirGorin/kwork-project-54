from aiogram import Router, Bot
from aiogram.types import Message
from database import get_param, get_user, set_inviter_id
from logging import getLogger
from utils import get_arg, get_menu, get_text_with_variables
from filters import CommandFilter, ButtonFilter
from my_types import User
from database import get_users, set_admin

router = Router()
logger = getLogger('handler_start')


@router.message(ButtonFilter('🎁 Получить подарок'))
@router.message(ButtonFilter('🧍 Режим пользователя'))
@router.message(CommandFilter('start'))
@router.message()
async def handler(message: Message, bot: Bot, user: User):
    admins = await get_users(is_admin=1)
    if not admins:
        await set_admin(user.user_id)
        user.is_admin = True

    text = await get_param('message_start')
    photo = await get_param('image_start')
    text = await get_text_with_variables(text=text,
                                         user_id=user.user_id,
                                         username=user.username,
                                         first_name=user.first_name,
                                         last_name=user.last_name)
    buttons = ['🔗 Реферальная ссылка', '🎁 Получить подарок']
    if user.is_admin:
        buttons.append('⚙️ Админ панель')
    menu = get_menu(buttons)

    try:
        await message.answer_photo(caption=text,
                                   photo=photo,
                                   reply_markup=menu)
    except:
        await message.answer(text=text,
                             reply_markup=menu)

    inviter_id_new = get_arg(message.text)
    if inviter_id_new and not user.inviter_id and inviter_id_new != user.user_id:
        await set_inviter_id(user.user_id, inviter_id_new)
        invaiter = await get_user(inviter_id_new)
        needed_refers = await get_param('needed_number_of_referrals')
        remain_refers = needed_refers - invaiter.current_refers
        if remain_refers > 0:
            text = await get_param('message_new_referral_other')
        elif remain_refers < 0:
            text = await get_param('message_after_getting_promocode')
        else:
            text = await get_param('message_getting_promocode')
        text = await get_text_with_variables(text=text,
                                             user_id=user.user_id,
                                             needed_refers=needed_refers,
                                             current_refers=invaiter.current_refers,
                                             remain_refers=remain_refers)
        await bot.send_message(chat_id=inviter_id_new,
                               text=text)
