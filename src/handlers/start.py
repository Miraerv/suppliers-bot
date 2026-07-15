from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src import texts
from src.config import Config
from src.keyboards.common import auth_keyboard, known_user_keyboard, schedule_keyboard
from src.services.suppliers import format_schedule_days, SupplierRepo
from src.states.schedule import ScheduleStates

router = Router(name="start")
# Поставщикский сценарий только в личке — в группе /start не отвечаем
router.message.filter(F.chat.type == ChatType.PRIVATE)


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    # Сброс FSM: /start — всегда «чистый вход» в сценарий
    await state.clear()

    assert message.from_user is not None
    known = suppliers.get(message.from_user.id)

    if known is not None and known.is_approved:
        if not known.has_schedule:
            await state.set_state(ScheduleStates.picking)
            await state.update_data(schedule_selected=[])
            await message.answer(
                texts.welcome_known(config.company_name, known.company_name),
            )
            await message.answer(
                texts.ask_schedule(),
                reply_markup=schedule_keyboard(set()),
            )
            return

        schedule_label = format_schedule_days(known.weekdays)
        await message.answer(
            texts.welcome_known(config.company_name, known.company_name)
            + f"\n\n📅 Расписание: <b>{schedule_label}</b>",
            reply_markup=known_user_keyboard(),
        )
        await message.answer(texts.wait_for_file())
        return

    if known is not None and known.is_pending:
        await message.answer(texts.already_pending(known.company_name))
        return

    await message.answer(
        texts.welcome(config.company_name),
        reply_markup=auth_keyboard(),
    )
