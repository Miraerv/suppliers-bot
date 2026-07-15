from __future__ import annotations

from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery, Message

from src import texts
from src.config import Config
from src.keyboards.common import CB_UPDATE_PRICE, auth_keyboard
from src.services.files import (
    describe_reject_reason,
    is_allowed_document,
    is_too_large,
)
from src.services.routing import accept_and_route
from src.services.suppliers import SupplierRepo
from src.timeutil import format_when

router = Router(name="price")
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


@router.callback_query(F.data == CB_UPDATE_PRICE)
async def on_update_price(
    callback: CallbackQuery,
    suppliers: SupplierRepo,
) -> None:
    await callback.answer()
    assert callback.from_user is not None
    assert callback.message is not None

    known = suppliers.get_approved(callback.from_user.id)
    if known is None:
        pending = suppliers.get(callback.from_user.id)
        if pending is not None and pending.is_pending:
            await callback.message.answer(texts.already_pending(pending.company_name))
            return
        await callback.message.answer(
            texts.need_auth(),
            reply_markup=auth_keyboard(),
        )
        return

    await callback.message.answer(texts.wait_for_file())


@router.message(F.document)
async def on_document(
    message: Message,
    bot: Bot,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    assert message.from_user is not None
    assert message.document is not None

    supplier = suppliers.get_approved(message.from_user.id)
    if supplier is None:
        pending = suppliers.get(message.from_user.id)
        if pending is not None and pending.is_pending:
            await message.answer(texts.already_pending(pending.company_name))
            return
        await message.answer(texts.need_auth(), reply_markup=auth_keyboard())
        return

    document = message.document

    if is_too_large(document, config.max_file_bytes):
        await message.answer(texts.file_too_large())
        return

    if not is_allowed_document(document):
        await message.answer(
            texts.bad_format(
                describe_reject_reason(message),
                config.manager_contacts,
            )
        )
        return

    when = format_when()
    await accept_and_route(
        bot=bot,
        document_file_id=document.file_id,
        original_filename=document.file_name,
        supplier=supplier,
        user=message.from_user,
        admin_chat_id=config.admin_chat_id,
        prices_dir=Path(config.data_dir) / "prices",
        when=when,
    )
    suppliers.mark_price_sent(message.from_user.id)

    await message.answer(texts.success())


@router.message(F.photo | F.video | F.audio | F.voice | F.sticker | F.text)
async def on_wrong_content(
    message: Message,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    """Любой «не документ» от уже известного поставщика — мягкая ошибка формата.

    Неавторизованных не спамим этим текстом на каждое сообщение:
    достаточно need_auth.
    """
    assert message.from_user is not None

    # /start и команды обрабатываются другими роутерами раньше; на всякий случай
    if message.text and message.text.startswith("/"):
        return

    supplier = suppliers.get_approved(message.from_user.id)
    if supplier is None:
        pending = suppliers.get(message.from_user.id)
        if pending is not None and pending.is_pending:
            await message.answer(texts.already_pending(pending.company_name))
            return
        await message.answer(texts.need_auth(), reply_markup=auth_keyboard())
        return

    await message.answer(
        texts.bad_format(
            describe_reject_reason(message),
            config.manager_contacts,
        )
    )
