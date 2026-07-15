from aiogram.fsm.state import State, StatesGroup


class ScheduleStates(StatesGroup):
    picking = State()
