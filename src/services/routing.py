"""Доставка принятого прайса во внутренний контур (MVP = закрытый чат закупок).

Слой специально отделён: завтра сюда можно добавить 1С / S3 / Google Drive,
не трогая хендлеры.
"""

from __future__ import annotations

from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, User

from src import texts
from src.services.files import make_stored_name
from src.services.suppliers import Supplier


async def accept_and_route(
    *,
    bot: Bot,
    document_file_id: str,
    original_filename: str | None,
    supplier: Supplier,
    user: User,
    admin_chat_id: int,
    prices_dir: Path,
    when: str,
    topic_id: int | None = None,
) -> str:
    """Скачать → переименовать → сохранить локально → отправить в чат закупок.

    Возвращает итоговое имя файла на диске.
    """
    prices_dir.mkdir(parents=True, exist_ok=True)
    stored_name = make_stored_name(supplier.company_name, original_filename)
    local_path = prices_dir / stored_name

    # bot.download ходит в Telegram File API (getFile + HTTPS download)
    await bot.download(document_file_id, destination=local_path)

    full_name = " ".join(
        p for p in (user.first_name or "", user.last_name or "") if p
    ).strip() or "—"
    caption = texts.admin_caption(
        supplier_name=supplier.company_name,
        username=user.username,
        full_name=full_name,
        when=when,
    )
    await bot.send_document(
        chat_id=admin_chat_id,
        message_thread_id=topic_id,
        document=FSInputFile(local_path, filename=stored_name),
        caption=caption,
    )
    return stored_name
