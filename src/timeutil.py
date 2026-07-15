"""Якутское время (Asia/Yakutsk, UTC+9, без перехода на летнее)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

YAKUTSK = timezone(timedelta(hours=9))


def now_yakutsk() -> datetime:
    return datetime.now(YAKUTSK)


def to_yakutsk(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(YAKUTSK)


def to_yakutsk_date(dt: datetime) -> date:
    return to_yakutsk(dt).date()


def format_when(dt: datetime | None = None) -> str:
    """15.07.2026 13:46 — для сообщений менеджерам/поставщику."""
    moment = dt or now_yakutsk()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=YAKUTSK)
    else:
        moment = moment.astimezone(YAKUTSK)
    return moment.strftime("%d.%m.%Y %H:%M")


def format_stamp(dt: datetime | None = None) -> str:
    """2026-07-15_13-46-31 — для имён файлов."""
    moment = dt or now_yakutsk()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=YAKUTSK)
    else:
        moment = moment.astimezone(YAKUTSK)
    return moment.strftime("%Y-%m-%d_%H-%M-%S")
