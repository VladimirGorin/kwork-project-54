from aiogram.filters.callback_data import CallbackData


class Automessage(CallbackData, prefix="automsg"):
    action: str
    value: int


class Subscribers(CallbackData, prefix="subscibers"):
    action: str
