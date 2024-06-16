from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, InlineKeyboardBuilder
from asyncio import sleep
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from database import get_user, get_param, get_users, block_user, get_automessages_and_users, get_result_sending
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from database import get_jobs, get_users, write_result_sending, set_state_job, create_job
from my_types import Job

variables = {
    'username': 'Юзернэйм пользователя',
    'first_name': 'Имя пользователя',
    'last_name': 'Фамилия пользователя',
    'invite_url': 'Пригласительная ссылка',
    'current_refers': 'Текущее количество рефералов',
    'needed_refers': 'Необходимое количество рефералов',
    'remain_refers': 'Осталось пригласить рефералов'
}
variables_str = '\n'.join(
    [f'<code>{{{key}}}</code> - {value}' for key, value in variables.items()])
commons = dict()


def get_arg(message_text: str) -> int:
    """Получение аргумента команды start"""
    if message_text:
        inviter_id_str = message_text[7:]
        if inviter_id_str.isdigit():
            return int(inviter_id_str)
    return 0


def get_menu(buttons: list) -> ReplyKeyboardMarkup:
    """Возвращает клавитатуру, сформированную по списку"""
    builder = ReplyKeyboardBuilder()
    if len(buttons) >= 3:
        cols = len(buttons) // 3
    else:
        cols = 1
    for button in buttons:
        builder.button(text=button)
    return builder.adjust(cols).as_markup(resize_keyboard=True)


def get_inline(buttons: list) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name, callback_data in buttons:
        builder.button(text=name, callback_data=callback_data)
    return builder.adjust(1).as_markup()


async def sending(message: Message, bot: Bot, anchors: dict):
    """Задача на рассылку"""
    users = await get_users()
    users = [user for user in users if user[4] == 0]
    text = message.html_text
    text_include_anchors = False
    for key in anchors.keys():
        if key in text:
            text_include_anchors = True
            break
    if text_include_anchors:
        if message.photo:
            photo = message.photo[-1].file_id
        else:
            photo = None
        data = [(*user, text, photo) for user in users]
        count_success = await personalized_sending(data=data,
                                                   bot=bot)
    else:
        count_success = await copy_message(message=message,
                                           users=users)
    count_users = len(users)
    text = (f'<b>Результаты рассылки</b>\n\n'
            f'Общее количество пользователей: {count_users}\n'
            f'Успешно отправлено: {count_success}\n'
            f'Не удалось отправить: {count_users - count_success}')
    await message.reply(text)


async def copy_message(message: Message, users: list) -> int:
    """Рассылка без персоноализации данных"""
    count_success = 0
    for user_id, *_ in users:
        while True:
            try:
                await message.copy_to(user_id)
                count_success += 1
                print(f'copy_message: {user_id} - success')
                break
            except TelegramRetryAfter as e:
                delay = e.retry_after
                print(f'copy_message: {user_id} - many flood')
                await sleep(delay)
            except TelegramForbiddenError:
                await block_user(user_id)
                print(f'copy_message: {user_id} - blocked')
                break
            except Exception as e:
                print(f'copy_message: {user_id} - {str(e)}')
                break
    return count_success


def get_delay_int(delay_str: str) -> int:
    weights = {'д': 86400, 'ч': 3600, 'м': 60, 'с': 1}
    delay_list = delay_str.split(' ')
    delay_int = 0
    for item in delay_list:
        value = int(item[:-1])
        key = item[-1:]
        delay_int += value * weights[key]
    return delay_int


def get_delay_str(delay_int: int) -> str:
    weights = {'д': 86400, 'ч': 3600, 'м': 60, 'с': 1}
    delay_list = []
    f = delay_int
    for key, value in weights.items():
        i, f = divmod(f, value)
        if i:
            delay_list.append(f'{i}{key}')
    return ' '.join(delay_list)


async def get_text_with_variables(text: str, user_id: int, **kwargs) -> str:
    """Возвращает текст с установленными переменными"""
    if not text:
        return text
    user_keys = {'username', 'first_name',
                 'last_name', 'current_refers', 'remain_refers'}
    params_keys = {'needed_refers', 'remain_refers'}
    remain_keys = {'remain_refers'}
    data = dict()
    for key in variables.keys():
        if key in text:
            data[key] = kwargs.get(key, None)
    data['invite_url'] = f'{commons["bot_url"]}?start={user_id}'
    empty_keys = {key for key, value in data.items() if not value}
    if empty_keys & user_keys:
        user = await get_user(user_id)
        data['username'] = user.username
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['current_refers'] = await get_param('needed_number_of_referrals')
    if empty_keys & params_keys:
        data['needed_refers'] = await get_param('needed_number_of_referrals')
    if empty_keys & remain_keys:
        remain = data['needed_refers'] - data['current_refers']
        data['remain_refers'] = remain if remain > 0 else 0
    return text.format(**data)


async def sending_job(job: Job, bot: Bot):
    needed_refers = await get_param('needed_number_of_referrals')
    if not job.users:
        job.users = await get_users(blocked=0)
        job.users = [(*user, job.message, job.photo) for user in job.users]
    for (user_id, username, first_name, last_name, blocked, inviter_id, count_refers, is_admin, created_at,
         text, photo) in job.users:
        text = await get_text_with_variables(text=text,
                                             user_id=user_id,
                                             needed_refers=needed_refers,
                                             username=username,
                                             first_name=first_name,
                                             last_name=last_name,
                                             count_refers=count_refers)
        while True:
            try:
                if photo:
                    await bot.send_photo(chat_id=user_id,
                                         caption=text,
                                         photo=photo)
                else:
                    await bot.send_message(chat_id=user_id,
                                           text=text)
                await write_result_sending(job.job_id, user_id, 'success')
                break
            except TelegramRetryAfter as e:
                delay = e.retry_after
                await write_result_sending(job.job_id, user_id, str(e))
                await sleep(delay)
            except TelegramForbiddenError as e:
                await block_user(user_id)
                await write_result_sending(job.job_id, user_id, str(e))
                break
            except Exception as e:
                await write_result_sending(job.job_id, user_id, str(e))
                break
    await set_state_job(job.job_id, 'Завершена')
    count_total, count_success, count_fail = await get_result_sending(job.job_id)
    report_text = (f"<b>Задача на рассылку №{job.job_id}</b>\n\n"
                   f"<b>Состояние:</b> {job.state}\n"
                   f"<b>Дата и время запуска:</b> {job.start[:25]}\n"
                   f"<b>Текст сообщения:</b>\n---\n{job.message}\n---\n\n"
                   f"<b>Всего пользователей:</b> {count_total}\n"
                   f"<b>Успешно отправлено:</b> {count_success}\n"
                   f"<b>Не отправлено:</b> {count_fail}\n")
    if job.photo:
        await bot.send_photo(chat_id=job.user_id,
                             caption=report_text,
                             photo=job.photo)
    else:
        await bot.send_message(chat_id=job.user_id,
                               text=report_text)


async def sender(scheduler: AsyncIOScheduler, bot: Bot):
    for job in await get_jobs():
        scheduler.add_job(func=sending_job,
                          trigger='date',
                          next_run_time=datetime.now() + timedelta(seconds=1),
                          args=(job, bot))
        await set_state_job(job.job_id, 'Обрабатывается')


async def create_jobs_automessage(interval: int):
    data = await get_automessages_and_users(interval)
    if data:
        await create_job(type='automessage',
                         start=datetime.now() + timedelta(seconds=1),
                         text=None,
                         photo=None,
                         user_id=None,
                         users=data)
