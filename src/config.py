from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path


@dataclass(frozen=True)
class Config:
    bot_token: str
    company_name: str
    admin_chat_id: int
    data_dir: Path
    manager_contacts: str
    # Напоминания о прайсе (якутское время), через запятую часы: "10,15"
    reminder_hours: tuple[int, ...]
    # Telegram API proxy (when api.telegram.org is blocked / flaky)
    use_tproxy: bool = False
    tproxy_base: str = "https://tg.michaelmironov122.online"
    max_file_bytes: int = 20 * 1024 * 1024
    allowed_extensions: tuple[str, ...] = (".xlsx", ".xls", ".csv")


def _require(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set (check .env)")
    return value


def _parse_hours(raw: str) -> tuple[int, ...]:
    hours: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        hour = int(part)
        if not 0 <= hour <= 23:
            raise RuntimeError(f"Invalid hour in REMINDER_HOURS: {hour}")
        hours.append(hour)
    return tuple(hours) if hours else (10,)


def load_config() -> Config:
    data_dir = Path(getenv("DATA_DIR", "data")).resolve()
    return Config(
        bot_token=_require("BOT_TOKEN"),
        company_name=getenv("COMPANY_NAME", "Boontar"),
        admin_chat_id=int(_require("ADMIN_CHAT_ID")),
        data_dir=data_dir,
        manager_contacts=getenv(
            "MANAGER_CONTACTS",
            "свяжитесь с вашим менеджером",
        ),
        reminder_hours=_parse_hours(getenv("REMINDER_HOURS", "10,15")),
        use_tproxy=getenv("USE_TPROXY", "false").lower() in ("1", "true", "yes"),
        tproxy_base=getenv(
            "TPROXY_BASE", "https://tg.michaelmironov122.online"
        ).rstrip("/"),
    )
