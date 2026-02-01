from aiogram.dispatcher.filters.state import State, StatesGroup


class Creation(StatesGroup):
    choosing_world = State()
    choosing_background = State()
    choosing_role = State()
    finished = State()
