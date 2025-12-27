from aiogram.dispatcher.filters.state import State, StatesGroup


class StudentState(StatesGroup):
    group = State()
    recaptcha = State()
    vote = State()
    get_vote = State()

