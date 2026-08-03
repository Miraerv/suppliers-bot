from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from src import texts
from src.config import Config
from src.keyboards.common import (
    CB_APPROVE_PREFIX,
    CB_AUTH,
    CB_REJECT_PREFIX,
    auth_keyboard,
    moderation_keyboard,
    schedule_keyboard,
)
from src.services.suppliers import STATUS_REJECTED, SupplierRepo
from src.services.topics import close_topic, create_supplier_topic, rename_topic
from src.states.auth import AuthStates

logger = logging.getLogger(__name__)

router = Router(name="auth")
# Сообщения авторизации (ИНН и т.п.) — только в личке.
# Callback approve/reject намеренно без этого фильтра: они жмутся в админ-группе.
router.message.filter(F.chat.type == ChatType.PRIVATE)


def _display_name(user: User) -> str:
    parts = [user.first_name or "", user.last_name or ""]
    name = " ".join(p for p in parts if p).strip()
    return name or "—"


def _moderator_label(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    return _display_name(user)


@router.callback_query(F.data == CB_AUTH, F.message.chat.type == ChatType.PRIVATE)
async def on_auth_click(
    callback: CallbackQuery,
    state: FSMContext,
    suppliers: SupplierRepo,
) -> None:
    """Inline-кнопка → CallbackQuery (не Message).

    Обязательно callback.answer() — иначе у пользователя «часики» на кнопке.
    """
    await callback.answer()
    assert callback.from_user is not None
    assert callback.message is not None

    known = suppliers.get(callback.from_user.id)
    if known is not None and known.is_approved:
        await callback.message.answer(texts.identified(known.company_name))
        await callback.message.answer(texts.wait_for_file())
        await state.clear()
        return

    if known is not None and known.is_pending:
        await callback.message.answer(texts.already_pending(known.company_name))
        await state.clear()
        return

    await state.set_state(AuthStates.waiting_inn)
    await callback.message.answer(texts.ask_inn())


@router.message(AuthStates.waiting_inn, F.text)
async def on_inn(
    message: Message,
    state: FSMContext,
    suppliers: SupplierRepo,
) -> None:
    assert message.from_user is not None
    assert message.text is not None

    inn_raw = message.text.strip()

    skip_tokens = {"-", "нет", "skip", "no", "—"}
    if inn_raw.lower() in skip_tokens:
        inn = None
    elif inn_raw.isdigit() and len(inn_raw) in (10, 12):
        inn = inn_raw
    else:
        await message.answer(texts.bad_inn())
        return

    existing = suppliers.get(message.from_user.id)
    if existing is not None and existing.is_approved:
        await state.clear()
        await message.answer(texts.identified(existing.company_name))
        await message.answer(texts.wait_for_file())
        return

    if existing is not None and existing.is_pending:
        await state.clear()
        await message.answer(texts.already_pending(existing.company_name))
        return

    await state.update_data(inn=inn)
    await state.set_state(AuthStates.waiting_company)
    await message.answer(texts.ask_company_name())


@router.message(AuthStates.waiting_inn)
async def on_inn_not_text(message: Message) -> None:
    await message.answer(texts.bad_inn())


@router.message(AuthStates.waiting_company, F.text)
async def on_company_name(
    message: Message,
    state: FSMContext,
    bot: Bot,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    assert message.from_user is not None
    assert message.text is not None

    company = message.text.strip()
    if len(company) < 2:
        await message.answer(texts.bad_company_name())
        return

    data = await state.get_data()
    inn = data.get("inn")

    user = message.from_user
    existing = suppliers.get(user.id)
    if existing is not None and existing.is_approved:
        await state.clear()
        await message.answer(texts.identified(existing.company_name))
        await message.answer(texts.wait_for_file())
        return

    if existing is not None and existing.is_pending:
        await state.clear()
        await message.answer(texts.already_pending(existing.company_name))
        return

    full_name = _display_name(user)
    supplier = suppliers.create_pending(
        telegram_id=user.id,
        company_name=company,
        inn=inn,
        username=user.username,
        full_name=full_name,
    )
    await state.clear()

    topic_id: int | None = None
    try:
        topic_id = await create_supplier_topic(
            bot,
            config.admin_chat_id,
            supplier.company_name,
            pending=True,
        )
        suppliers.set_topic_id(user.id, topic_id)
    except Exception:
        logger.exception(
            "Failed to create forum topic for user=%s in chat=%s",
            user.id,
            config.admin_chat_id,
        )

    try:
        await bot.send_message(
            chat_id=config.admin_chat_id,
            message_thread_id=topic_id,
            text=texts.moderation_request(
                company_name=supplier.company_name,
                inn=supplier.inn,
                username=user.username,
                full_name=full_name,
            ),
            reply_markup=moderation_keyboard(user.id),
        )
    except Exception:
        logger.exception(
            "Failed to send moderation request to admin_chat_id=%s user=%s",
            config.admin_chat_id,
            user.id,
        )
        await message.answer(
            "Не удалось отправить заявку менеджерам. "
            f"Попробуйте позже или {config.manager_contacts}."
        )
        return

    await message.answer(texts.pending_moderation(supplier.company_name))


@router.message(AuthStates.waiting_company)
async def on_company_name_not_text(message: Message) -> None:
    await message.answer(
        "Нужен текст: юридическое название компании или ИНН. "
        "Попробуйте ещё раз."
    )


@router.callback_query(F.data.startswith(CB_APPROVE_PREFIX))
async def on_approve(
    callback: CallbackQuery,
    bot: Bot,
    suppliers: SupplierRepo,
) -> None:
    assert callback.from_user is not None
    assert callback.data is not None
    assert callback.message is not None

    try:
        telegram_id = int(callback.data.removeprefix(CB_APPROVE_PREFIX))
    except ValueError:
        await callback.answer("Некорректные данные кнопки", show_alert=True)
        return

    supplier = suppliers.get(telegram_id)
    if supplier is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    if supplier.is_approved:
        await callback.answer("Уже одобрено")
        await callback.message.edit_text(
            texts.moderation_decided(
                approved=True,
                company_name=supplier.company_name,
                inn=supplier.inn,
                username=supplier.username,
                full_name=supplier.full_name or "—",
                moderator=_moderator_label(callback.from_user),
            )
        )
        return

    approved = suppliers.approve(telegram_id)
    if approved is None:
        await callback.answer("Не удалось одобрить", show_alert=True)
        return

    await callback.answer("Одобрено")
    await callback.message.edit_text(
        texts.moderation_decided(
            approved=True,
            company_name=approved.company_name,
            inn=approved.inn,
            username=approved.username,
            full_name=approved.full_name or "—",
            moderator=_moderator_label(callback.from_user),
        )
    )

    if approved.topic_id is not None:
        try:
            await rename_topic(
                callback.bot,
                callback.message.chat.id,
                approved.topic_id,
                approved.company_name,
            )
        except Exception:
            logger.exception(
                "Failed to rename topic %s for user %s",
                approved.topic_id,
                telegram_id,
            )

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=texts.approved_notify(approved.company_name),
        )
        # Сразу просим выбрать календарь дней отправки прайса
        await bot.send_message(
            chat_id=telegram_id,
            text=texts.ask_schedule(),
            reply_markup=schedule_keyboard(set()),
        )
    except Exception:
        logger.exception("Failed to notify user %s about approval", telegram_id)


@router.callback_query(F.data.startswith(CB_REJECT_PREFIX))
async def on_reject(
    callback: CallbackQuery,
    bot: Bot,
    suppliers: SupplierRepo,
) -> None:
    assert callback.from_user is not None
    assert callback.data is not None
    assert callback.message is not None

    try:
        telegram_id = int(callback.data.removeprefix(CB_REJECT_PREFIX))
    except ValueError:
        await callback.answer("Некорректные данные кнопки", show_alert=True)
        return

    supplier = suppliers.get(telegram_id)
    if supplier is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    if supplier.status == STATUS_REJECTED:
        await callback.answer("Уже отклонено")
        await callback.message.edit_text(
            texts.moderation_decided(
                approved=False,
                company_name=supplier.company_name,
                inn=supplier.inn,
                username=supplier.username,
                full_name=supplier.full_name or "—",
                moderator=_moderator_label(callback.from_user),
            )
        )
        return

    rejected = suppliers.reject(telegram_id)
    if rejected is None:
        await callback.answer("Не удалось отклонить", show_alert=True)
        return

    await callback.answer("Отклонено")
    await callback.message.edit_text(
        texts.moderation_decided(
            approved=False,
            company_name=rejected.company_name,
            inn=rejected.inn,
            username=rejected.username,
            full_name=rejected.full_name or "—",
            moderator=_moderator_label(callback.from_user),
        )
    )

    if rejected.topic_id is not None:
        try:
            await close_topic(
                callback.bot,
                callback.message.chat.id,
                rejected.topic_id,
            )
        except Exception:
            logger.exception(
                "Failed to close topic %s for user %s",
                rejected.topic_id,
                telegram_id,
            )

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=texts.rejected_notify(rejected.company_name),
            reply_markup=auth_keyboard(),
        )
    except Exception:
        logger.exception("Failed to notify user %s about rejection", telegram_id)
