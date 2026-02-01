from aiogram.dispatcher.filters.state import State, StatesGroup


class CharacterCreation(StatesGroup):
    waiting_for_xp = State()
    choosing_homeworld = State()
    rolling_characteristics = State()
    assigning_characteristics = State()
