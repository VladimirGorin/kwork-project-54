from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    Default = State()
    WaitingNumberReferals = State()
    WaitingStartMessage = State()
    WaitingNewReferal1LeftMessage = State()
    WaitingNewReferalOtherMessage = State()
    WaitingGettingPromocodeMessage = State()
    WaitingAfterGettingPromocodeMessage = State()
    WaitingSendingMessage = State()
    WaitingSendingDatetime = State()
    WaitingAutomessageDelay = State()
    WaitingAutomessage = State()
    WaitingGetGiftFailMessage = State()
    WaitingGetGiftSuccessMessage = State()
    ContolMessages = State()
