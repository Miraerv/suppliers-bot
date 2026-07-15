from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    """Состояния диалога авторизации.

    FSM в aiogram — это state machine:
    - state хранится в storage (Memory / Redis) по ключу (bot_id, chat_id, user_id)
    - фильтр StateFilter(AuthStates.waiting_company) матчит только в этом шаге
    """

    waiting_company = State()
