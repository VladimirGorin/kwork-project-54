from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database import get_user, create_user, update_user


class OuterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        event_from_user = data.get('event_from_user')
        user_id = event_from_user.id
        username = event_from_user.username
        first_name = event_from_user.first_name
        last_name = event_from_user.last_name

        user = await get_user(user_id)
        if not user:
            user = await create_user(user_id, username, first_name, last_name)
        elif (user.blocked
              or user.username != username
              or user.first_name != first_name
              or user.last_name != last_name):
            user = await update_user(user_id, username, first_name, last_name, user)
        data['user'] = user
        return await handler(event, data)
