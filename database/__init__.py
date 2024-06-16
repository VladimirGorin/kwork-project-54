from config import Config
from aiosqlite import connect
from my_types import User, Job
from typing import Optional
from datetime import datetime
from json import loads, dumps

database_path = Config.db


async def get_user(user_id: int) -> Optional[User]:
    """Возвращает информацию о пользователе из базы"""
    sql = ("SELECT id, username, first_name, last_name, blocked, inviter_id, created_at, count_refers, is_admin "
           "FROM v_user WHERE id = ? LIMIT 1")
    async with connect(database_path) as db:
        async with db.execute(sql, (user_id,)) as cursor:
            user = await cursor.fetchone()
    if user:
        user_id, username, first_name, last_name, blocked, inviter_id, created_at, count_refers, is_admin = user
        return User(user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    blocked=bool(blocked),
                    inviter_id=inviter_id,
                    current_refers=count_refers,
                    created_at=created_at,
                    is_admin=bool(is_admin))
    else:
        return None


async def set_admin(user_id: int):
    sql = "UPDATE t_user SET is_admin = 1 WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (user_id,))
        await db.commit()


async def create_user(user_id: int, username: str, first_name: str, last_name: str) -> User:
    sql = "INSERT OR IGNORE INTO t_user (id, username, first_name, last_name) VALUES (?, ?, ?, ?)"
    async with connect(database_path) as db:
        await db.execute(sql, (user_id, username, first_name, last_name))
        await db.commit()
    return User(user_id=user_id,
                username=username,
                last_name=last_name,
                first_name=first_name)


async def update_user(user_id: int, username: str, first_name: str, last_name: str, user: User) -> User:
    blocked = False
    sql = "UPDATE t_user SET username = ?, first_name = ?, last_name = ?, blocked = ? WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (username, first_name, last_name, blocked, user_id))
        await db.commit()
    return User(user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                blocked=blocked,
                inviter_id=user.inviter_id,
                current_refers=user.current_refers,
                created_at=user.created_at,
                is_admin=user.is_admin)


async def get_param(code: str):
    """Получение значения параметрам по коду"""
    sql = "SELECT value FROM t_param WHERE code = ?"
    async with connect(database_path) as db:
        async with db.execute(sql, (code,)) as cursor:
            (data,) = await cursor.fetchone()
            if data:
                return int(data) if data.isdigit() else data


async def update_param(code: str, value: str) -> None:
    """Обновление значения параметра"""
    sql = "UPDATE t_param SET value = ? WHERE code = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (value, code))
        await db.commit()


async def get_users(**kwargs) -> list:
    """Получение списка пользователей бота"""
    if kwargs:
        where_str = ' AND ' + (' AND '.join([f'{key} = "{value}"' for key, value in kwargs.items()]))
    else:
        where_str = ''
    sql = f"""
    SELECT id, username, first_name, last_name, blocked, inviter_id, count_refers, is_admin, created_at
    FROM v_user 
    WHERE 1 = 1 {where_str}
    """
    async with connect(database_path) as db:
        async with db.execute(sql) as cursor:
            users = await cursor.fetchall()
            return users


async def block_user(user_id: int) -> None:
    """Установка для юзера признака блокирования"""
    sql = "UPDATE t_user SET blocked = 1 WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (user_id,))
        await db.commit()


async def unblock_user(user_id: int) -> None:
    """Снятие для юзера признака блокирования"""
    sql = "UPDATE t_user SET blocked = 0 WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (user_id,))
        await db.commit()


async def get_automessages() -> list:
    sql = "SELECT id, message, photo, delay FROM t_automessage WHERE deleted = 0 ORDER BY delay"
    async with connect(database_path) as db:
        async with db.execute(sql) as cursor:
            automessages = await cursor.fetchall()
            return automessages


async def get_automessage(automessage_id: int) -> list:
    sql = "SELECT id, message, photo, delay FROM t_automessage WHERE id = ? LIMIT 1"
    async with connect(database_path) as db:
        async with db.execute(sql, (automessage_id,)) as cursor:
            automessage = await cursor.fetchone()
            return automessage


async def create_automessage(text: str, photo: str, delay: int):
    sql = "INSERT INTO t_automessage (message, photo, delay) VALUES (?, ?, ?)"
    async with connect(database_path) as db:
        await db.execute(sql, (text, photo, delay))
        await db.commit()


async def delete_automessage(automessage_id: int) -> None:
    sql = "UPDATE t_automessage SET deleted = 1 WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (automessage_id,))
        await db.commit()


async def recovery_automessage(automessage_id: int) -> None:
    sql = "UPDATE t_automessage SET deleted = 0 WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (automessage_id,))
        await db.commit()


async def get_automessages_and_users(interval: int) -> list:
    sql = """
    SELECT u.id, username, first_name, last_name, blocked, u.inviter_id, count_refers, is_admin, 
    created_at, a.message, a.photo
    FROM t_automessage a 
    INNER JOIN v_user u 
    ON strftime('%s', u.created_at) + a.delay BETWEEN strftime('%s', datetime('now', 'localtime')) - ? 
    AND strftime('%s', datetime('now', 'localtime')) * 1
    WHERE deleted = 0
    AND u.blocked = 0
    """
    async with connect(database_path) as db:
        async with db.execute(sql, (interval,)) as cursor:
            data = await cursor.fetchall()
            return data


async def set_inviter_id(user_id: int, inviter_id: int):
    sql = "UPDATE t_user SET inviter_id = ? WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (inviter_id, user_id))
        await db.commit()


async def create_job(type: str,
                     start: datetime,
                     text: str,
                     photo: str,
                     user_id: int,
                     users: list = [],
                     message_id: int = None):
    state = 'Создана'
    users = dumps(users, ensure_ascii=False)
    sql = ("INSERT INTO t_job (type, start, message, photo, state, user_id, users, message_id) "
           "VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
    async with connect(database_path) as db:
        async with db.execute(sql, (type, start, text, photo, state, user_id, users, message_id)) as cursor:
            job_id = cursor.lastrowid
        await db.commit()
        return job_id


async def update_job(job_id: int, text: str, photo: str, start: datetime):
    pass


async def set_state_job(job_id: int, state: str):
    sql = "UPDATE t_job SET state = ? WHERE id = ?"
    async with connect(database_path) as db:
        await db.execute(sql, (state, job_id))
        await db.commit()


async def get_job(job_id: int) -> Job:
    sql = ("SELECT id, type, start, message, photo, created, state, user_id, users, message_id FROM t_job "
           "WHERE id = ? LIMIT 1")
    async with connect(database_path) as db:
        async with db.execute(sql, (job_id,)) as cursor:
            job = await cursor.fetchone()
    if job:
        job_id, job_type, start, message, photo, created, state, user_id, users, message_id = job
        return Job(job_id=job_id,
                   job_type=job_type,
                   start=start,
                   message=message,
                   photo=photo,
                   created_at=created,
                   state=state,
                   user_id=user_id,
                   users=users)


async def get_jobs() -> list:
    state = 'Создана'
    sql = """
        SELECT id, "type", "start", message, photo, created, state, user_id, users, message_id
        FROM t_job WHERE state = ? AND start <= datetime('now', 'localtime')
    """
    async with connect(database_path) as db:
        async with db.execute(sql, (state,)) as cursor:
            return [
                Job(job_id=job_id,
                    job_type=job_type,
                    start=start,
                    message=message,
                    photo=photo,
                    created_at=created,
                    state=state,
                    user_id=user_id,
                    users=loads(users) if users else None,
                    message_id=message_id)
                for job_id, job_type, start, message, photo, created, state, user_id, users, message_id
                in await cursor.fetchall()
            ]


async def write_result_sending(job_id: int, user_id: int, result: str):
    sql = "INSERT INTO t_sending (job_id, user_id, result) VALUES (?, ?, ?)"
    async with connect(database_path) as db:
        await db.execute(sql, (job_id, user_id, result))
        await db.commit()


async def get_result_sending(job_id: int) -> tuple:
    sql = """
        SELECT COUNT(1) AS count_total, 
        IFNULL(SUM(CASE WHEN result == 'success' THEN 1 ELSE 0 END), 0) AS count_success
        FROM t_sending 
        WHERE id IN (
        SELECT MAX(id)
        FROM t_sending 
        WHERE job_id = ?
        GROUP BY user_id)
    """
    async with connect(database_path) as db:
        async with db.execute(sql, (job_id,)) as cursor:
            count_total, count_success = await cursor.fetchone()
    return count_total, count_success, count_total - count_success
