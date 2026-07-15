from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from src import texts

logger = logging.getLogger(__name__)

router = Router(name="group")


@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_bot_added(event: ChatMemberUpdated) -> None:
    """Когда бота добавляют в группу/канал — сразу присылаем chat id."""
    chat = event.chat
    if chat.type not in {"group", "supergroup", "channel"}:
        return

    logger.info(
        "Bot added to %s chat_id=%s title=%r",
        chat.type,
        chat.id,
        chat.title,
    )

    try:
        await event.answer(texts.group_chat_id(chat.id, chat.title))
    except Exception:
        # Нет права писать (канал без post) — ID всё равно в логах
        logger.exception(
            "Cannot send chat id to chat_id=%s (missing post/send rights?)",
            chat.id,
        )
