"""Валидация и именование прайс-файлов — чистая логика без Telegram-объектов где возможно."""

from __future__ import annotations

import re
from pathlib import Path

from aiogram.types import Document, Message

from src.timeutil import format_stamp

ALLOWED_EXTENSIONS = (".xlsx", ".xls", ".csv")
MAX_FILE_BYTES = 20 * 1024 * 1024


def extension_of(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def is_allowed_document(document: Document) -> bool:
    return extension_of(document.file_name) in ALLOWED_EXTENSIONS


def is_too_large(document: Document, limit: int = MAX_FILE_BYTES) -> bool:
    size = document.file_size or 0
    return size > limit


def slugify_company(name: str) -> str:
    """ИмяПоставщика для файла: без пробелов и опасных символов."""
    cleaned = re.sub(r"[^\w\-]+", "_", name.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:80] or "supplier"


def make_stored_name(company_name: str, original_filename: str | None) -> str:
    ext = extension_of(original_filename) or ".xlsx"
    return f"{slugify_company(company_name)}_{format_stamp()}{ext}"


def describe_reject_reason(message: Message) -> str:
    """Человекочитаемое «что прислали» для текста ошибки."""
    if message.photo:
        return "картинку"
    if message.video or message.video_note:
        return "видео"
    if message.voice or message.audio:
        return "аудио"
    if message.sticker:
        return "стикер"
    if message.document:
        ext = extension_of(message.document.file_name) or "файл без расширения"
        mime = message.document.mime_type or "unknown"
        if ext == ".pdf" or (mime and "pdf" in mime):
            return "PDF"
        return f"файл ({ext}, {mime})"
    if message.text:
        text = message.text.lower()
        if any(
            host in text
            for host in (
                "disk.yandex",
                "yadi.sk",
                "docs.google",
                "drive.google",
                "dropbox.com",
                "http://",
                "https://",
            )
        ):
            return "ссылку (нужен именно файл-документ, не ссылка на диск)"
        return "текст"
    return "сообщение неподдерживаемого типа"
