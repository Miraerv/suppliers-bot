"""Пересылка сообщений между админами (в форум-топиках) и поставщиками.

- Админ реплаит на сообщение бота в топике → поставщику в личку
- Поставщик пишет боту → в форум-топик (реализовано в price.py)
"""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.types import Message

from src.config import Config
from src.services.suppliers import SupplierRepo

logger = logging.getLogger(__name__)

router = Router(name="chat")


@router.message(F.is_topic_message == True)
async def on_admin_reply_in_topic(
    message: Message,
    bot: Bot,
    config: Config,
    suppliers: SupplierRepo,
) -> None:
    if message.chat.id != config.admin_chat_id:
        return
    if message.reply_to_message is None:
        return
    if message.reply_to_message.from_user is None:
        return
    if message.reply_to_message.from_user.id != bot.id:
        return
    if message.reply_to_message.message_id == message.message_thread_id:
        return

    topic_id = message.message_thread_id
    if topic_id is None:
        return

    supplier = suppliers.get_by_topic_id(topic_id)
    if supplier is None:
        return

    try:
        await message.copy_to(chat_id=supplier.telegram_id)
    except Exception:
        logger.exception(
            "Failed to forward admin reply to supplier telegram_id=%s",
            supplier.telegram_id,
        )
