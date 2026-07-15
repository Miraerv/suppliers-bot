"""Админ-команды: работают в группе ADMIN_CHAT_ID (и /help ещё в личке)."""

from __future__ import annotations

import logging

from aiogram import Bot, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src import texts
from src.config import Config
from src.services.suppliers import format_schedule_days, SupplierRepo

logger = logging.getLogger(__name__)

router = Router(name="admin")

# Telegram лимит сообщения ~4096; оставляем запас под HTML
_MAX_MESSAGE_CHARS = 3500


def _is_admin_chat(message: Message, config: Config) -> bool:
    return message.chat.id == config.admin_chat_id


async def _reply_chunks(message: Message, body: str) -> None:
    """Отправить длинный текст частями, не разрывая посреди строки."""
    if len(body) <= _MAX_MESSAGE_CHARS:
        await message.answer(body)
        return

    chunk: list[str] = []
    size = 0
    for line in body.split("\n"):
        # +1 за перевод строки при склейке
        add = len(line) + (1 if chunk else 0)
        if chunk and size + add > _MAX_MESSAGE_CHARS:
            await message.answer("\n".join(chunk))
            chunk = [line]
            size = len(line)
        else:
            chunk.append(line)
            size += add
    if chunk:
        await message.answer("\n".join(chunk))


@router.message(Command("help"))
async def cmd_help(message: Message, config: Config) -> None:
    if message.chat.type == ChatType.PRIVATE:
        await message.answer(texts.help_supplier(config.company_name))
        return
    if _is_admin_chat(message, config):
        await message.answer(texts.help_admin())


@router.message(Command("suppliers"))
async def cmd_suppliers(
    message: Message,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    if not _is_admin_chat(message, config):
        return

    rows = suppliers.list_all()
    if not rows:
        await message.answer(texts.admin_suppliers_empty())
        return

    parts = [texts.admin_suppliers_header(len(rows))]
    for i, s in enumerate(rows, start=1):
        parts.append(
            texts.admin_supplier_line(
                index=i,
                company_name=s.company_name,
                status=s.status,
                telegram_id=s.telegram_id,
                username=s.username,
                full_name=s.full_name,
                schedule_label=format_schedule_days(s.weekdays),
            )
        )
    await _reply_chunks(message, "".join(parts))


@router.message(Command("bind"))
async def cmd_bind(
    message: Message,
    command: CommandObject,
    bot: Bot,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    if not _is_admin_chat(message, config):
        return

    args = (command.args or "").strip()
    if not args:
        await message.answer(texts.admin_bind_usage())
        return

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(texts.admin_bind_usage())
        return

    raw_id, company = parts[0].strip(), parts[1].strip()
    try:
        telegram_id = int(raw_id)
    except ValueError:
        await message.answer(texts.admin_bad_telegram_id())
        return

    if len(company) < 2:
        await message.answer("Слишком короткое название компании / ИНН.")
        return

    existed = suppliers.get(telegram_id)
    # Если админ ответил на сообщение пользователя — подтянем username/имя
    username: str | None = None
    full_name: str | None = None
    reply_user = message.reply_to_message.from_user if message.reply_to_message else None
    if reply_user is not None and reply_user.id == telegram_id:
        username = reply_user.username
        name_parts = [reply_user.first_name or "", reply_user.last_name or ""]
        full_name = " ".join(p for p in name_parts if p).strip() or None

    bound = suppliers.bind(
        telegram_id,
        company,
        username=username,
        full_name=full_name,
    )
    await message.answer(
        texts.admin_bind_ok(
            telegram_id=bound.telegram_id,
            company_name=bound.company_name,
            status=bound.status,
            created=existed is None,
        )
    )

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=texts.admin_bind_notify(bound.company_name),
        )
    except Exception:
        logger.info(
            "Could not notify user %s about bind (blocked bot or never started)",
            telegram_id,
        )


@router.message(Command("unbind"))
async def cmd_unbind(
    message: Message,
    command: CommandObject,
    bot: Bot,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    if not _is_admin_chat(message, config):
        return

    args = (command.args or "").strip()
    if not args:
        await message.answer(texts.admin_unbind_usage())
        return

    raw_id = args.split(maxsplit=1)[0].strip()
    try:
        telegram_id = int(raw_id)
    except ValueError:
        await message.answer(texts.admin_bad_telegram_id())
        return

    existing = suppliers.get(telegram_id)
    if existing is None:
        await message.answer(texts.admin_unbind_not_found(telegram_id))
        return

    company_name = existing.company_name
    suppliers.unbind(telegram_id)
    await message.answer(texts.admin_unbind_ok(telegram_id, company_name))

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=texts.admin_unbind_notify(),
        )
    except Exception:
        logger.info(
            "Could not notify user %s about unbind (blocked bot or never started)",
            telegram_id,
        )
