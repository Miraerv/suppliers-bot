"""Выбор дней недели, когда поставщик должен присылать прайс."""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src import texts
from src.config import Config
from src.keyboards.common import (
    CB_SCHEDULE,
    CB_SCHEDULE_PRESET_PREFIX,
    CB_SCHEDULE_SAVE,
    CB_SCHEDULE_TOGGLE_PREFIX,
    SCHEDULE_PRESETS,
    known_user_keyboard,
    schedule_keyboard,
)
from src.services.suppliers import format_schedule_days, SupplierRepo
from src.states.schedule import ScheduleStates

logger = logging.getLogger(__name__)

router = Router(name="schedule")
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


async def _open_picker(
    callback: CallbackQuery,
    state: FSMContext,
    suppliers: SupplierRepo,
    *,
    seed_from_db: bool,
) -> None:
    assert callback.from_user is not None
    assert callback.message is not None

    known = suppliers.get_approved(callback.from_user.id)
    if known is None:
        await callback.answer("Сначала нужна авторизация", show_alert=True)
        return

    if seed_from_db:
        selected = set(known.weekdays)
        await state.update_data(schedule_selected=sorted(selected))
    else:
        data = await state.get_data()
        selected = set(data.get("schedule_selected") or [])

    await state.set_state(ScheduleStates.picking)
    current = format_schedule_days(known.weekdays) if known.has_schedule else None
    await callback.message.answer(
        texts.ask_schedule(current),
        reply_markup=schedule_keyboard(selected),
    )
    await callback.answer()


@router.callback_query(F.data == CB_SCHEDULE)
async def on_open_schedule(
    callback: CallbackQuery,
    state: FSMContext,
    suppliers: SupplierRepo,
) -> None:
    await _open_picker(callback, state, suppliers, seed_from_db=True)


@router.callback_query(F.data.startswith(CB_SCHEDULE_TOGGLE_PREFIX))
async def on_toggle_day(
    callback: CallbackQuery,
    state: FSMContext,
    suppliers: SupplierRepo,
) -> None:
    assert callback.from_user is not None
    assert callback.data is not None
    assert callback.message is not None

    if suppliers.get_approved(callback.from_user.id) is None:
        await callback.answer("Сначала нужна авторизация", show_alert=True)
        return

    try:
        day = int(callback.data.removeprefix(CB_SCHEDULE_TOGGLE_PREFIX))
    except ValueError:
        await callback.answer("Ошибка кнопки", show_alert=True)
        return
    if day < 0 or day > 6:
        await callback.answer("Ошибка кнопки", show_alert=True)
        return

    data = await state.get_data()
    selected = set(data.get("schedule_selected") or [])
    if day in selected:
        selected.remove(day)
    else:
        selected.add(day)
    await state.update_data(schedule_selected=sorted(selected))
    await state.set_state(ScheduleStates.picking)

    await callback.message.edit_reply_markup(reply_markup=schedule_keyboard(selected))
    await callback.answer()


@router.callback_query(F.data.startswith(CB_SCHEDULE_PRESET_PREFIX))
async def on_preset(
    callback: CallbackQuery,
    state: FSMContext,
    suppliers: SupplierRepo,
) -> None:
    assert callback.from_user is not None
    assert callback.data is not None
    assert callback.message is not None

    if suppliers.get_approved(callback.from_user.id) is None:
        await callback.answer("Сначала нужна авторизация", show_alert=True)
        return

    preset_id = callback.data.removeprefix(CB_SCHEDULE_PRESET_PREFIX)
    days = SCHEDULE_PRESETS.get(preset_id)
    if days is None:
        await callback.answer("Неизвестный пресет", show_alert=True)
        return

    selected = set(days)
    await state.update_data(schedule_selected=sorted(selected))
    await state.set_state(ScheduleStates.picking)
    await callback.message.edit_reply_markup(reply_markup=schedule_keyboard(selected))
    await callback.answer(format_schedule_days(selected))


@router.callback_query(F.data == CB_SCHEDULE_SAVE)
async def on_save_schedule(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    assert callback.from_user is not None
    assert callback.message is not None

    known = suppliers.get_approved(callback.from_user.id)
    if known is None:
        await callback.answer("Сначала нужна авторизация", show_alert=True)
        return

    data = await state.get_data()
    selected = set(data.get("schedule_selected") or [])
    if not selected:
        await callback.answer(texts.schedule_need_days(), show_alert=True)
        return

    updated = suppliers.set_schedule(callback.from_user.id, selected)
    await state.clear()
    label = format_schedule_days(selected)

    await callback.message.edit_text(texts.schedule_saved(label))
    await callback.message.answer(
        texts.wait_for_file(),
        reply_markup=known_user_keyboard(),
    )
    await callback.answer("Сохранено")

    supplier = updated or known
    user = callback.from_user
    full_name = " ".join(
        p for p in (user.first_name or "", user.last_name or "") if p
    ).strip() or (supplier.full_name or "—")
    try:
        await bot.send_message(
            chat_id=config.admin_chat_id,
            message_thread_id=supplier.topic_id,
            text=texts.admin_schedule_set(
                company_name=supplier.company_name,
                username=user.username or supplier.username,
                full_name=full_name,
                days_label=label,
            ),
        )
    except Exception:
        logger.exception(
            "Failed to notify admin about schedule for telegram_id=%s",
            user.id,
        )
