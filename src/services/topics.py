"""Обёртки над Telegram Bot API для работы с темами форума."""

from __future__ import annotations

import logging

from aiogram import Bot

logger = logging.getLogger(__name__)


async def create_supplier_topic(
    bot: Bot,
    chat_id: int,
    company_name: str,
    *,
    pending: bool = False,
) -> int:
    name = f"{company_name} (на модерации)" if pending else company_name
    result = await bot.create_forum_topic(chat_id=chat_id, name=name)
    logger.info(
        "Created topic '%s' (thread_id=%s) in chat %s",
        name,
        result.message_thread_id,
        chat_id,
    )
    return result.message_thread_id


async def rename_topic(
    bot: Bot,
    chat_id: int,
    topic_id: int,
    name: str,
) -> None:
    await bot.edit_forum_topic(
        chat_id=chat_id,
        message_thread_id=topic_id,
        name=name,
    )
    logger.info("Renamed topic %s to '%s' in chat %s", topic_id, name, chat_id)


async def close_topic(
    bot: Bot,
    chat_id: int,
    topic_id: int,
) -> None:
    await bot.close_forum_topic(
        chat_id=chat_id,
        message_thread_id=topic_id,
    )
    logger.info("Closed topic %s in chat %s", topic_id, chat_id)
