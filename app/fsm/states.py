from aiogram.fsm.state import StatesGroup, State


class MenuSG(StatesGroup):
    start = State()
    about = State()


class OwnerSG(StatesGroup):
    settings = State()
