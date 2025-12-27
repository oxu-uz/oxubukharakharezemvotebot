from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminState(StatesGroup):
    admin = State()
    area = State()
    exel_area = State()
    exel_area_seed = State()

