"""Персистентная привязка Telegram user → компания поставщика.

Не путать с FSM:
- FSM = «на каком шаге диалога сейчас» (эфемерно, можно MemoryStorage)
- SupplierRepo = «кто этот user навсегда» (SQLite, переживает рестарт)

Статусы:
- pending  — заявка на модерации
- approved — можно слать прайсы
- rejected — отклонено (можно подать снова)

Расписание:
- schedule_days — дни недели 0=Пн … 6=Вс через запятую, например "0,2,4"
- last_price_at / last_reminder_at — ISO UTC, для «заёбывания» о прайсе
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from src.timeutil import to_yakutsk_date

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

WEEKDAY_LABELS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")


def parse_schedule_days(raw: str | None) -> frozenset[int]:
    if not raw or not raw.strip():
        return frozenset()
    days: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            day = int(part)
        except ValueError:
            continue
        if 0 <= day <= 6:
            days.add(day)
    return frozenset(days)


def encode_schedule_days(days: set[int] | frozenset[int]) -> str:
    return ",".join(str(d) for d in sorted(days) if 0 <= d <= 6)


def format_schedule_days(days: set[int] | frozenset[int]) -> str:
    if not days:
        return "не задано"
    return ", ".join(WEEKDAY_LABELS[d] for d in sorted(days) if 0 <= d <= 6)


@dataclass(frozen=True)
class Supplier:
    telegram_id: int
    company_name: str
    status: str
    username: str | None
    full_name: str | None
    schedule_days: str | None
    last_price_at: str | None
    last_reminder_at: str | None
    created_at: str
    updated_at: str

    @property
    def is_approved(self) -> bool:
        return self.status == STATUS_APPROVED

    @property
    def is_pending(self) -> bool:
        return self.status == STATUS_PENDING

    @property
    def weekdays(self) -> frozenset[int]:
        return parse_schedule_days(self.schedule_days)

    @property
    def has_schedule(self) -> bool:
        return bool(self.weekdays)

    def price_sent_on(self, day: date) -> bool:
        if not self.last_price_at:
            return False
        try:
            sent = datetime.fromisoformat(self.last_price_at)
        except ValueError:
            return False
        return to_yakutsk_date(sent) == day

    def reminded_on(self, day: date) -> bool:
        if not self.last_reminder_at:
            return False
        try:
            reminded = datetime.fromisoformat(self.last_reminder_at)
        except ValueError:
            return False
        return to_yakutsk_date(reminded) == day


class SupplierRepo:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS suppliers (
                    telegram_id INTEGER PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'approved',
                    username TEXT,
                    full_name TEXT,
                    schedule_days TEXT,
                    last_price_at TEXT,
                    last_reminder_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            cols = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(suppliers)").fetchall()
            }
            migrations = {
                "status": "ALTER TABLE suppliers ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'",
                "username": "ALTER TABLE suppliers ADD COLUMN username TEXT",
                "full_name": "ALTER TABLE suppliers ADD COLUMN full_name TEXT",
                "schedule_days": "ALTER TABLE suppliers ADD COLUMN schedule_days TEXT",
                "last_price_at": "ALTER TABLE suppliers ADD COLUMN last_price_at TEXT",
                "last_reminder_at": "ALTER TABLE suppliers ADD COLUMN last_reminder_at TEXT",
            }
            for col, sql in migrations.items():
                if col not in cols:
                    conn.execute(sql)

    def _row_to_supplier(self, row: sqlite3.Row) -> Supplier:
        keys = set(row.keys())

        def col(name: str) -> str | None:
            return row[name] if name in keys else None

        return Supplier(
            telegram_id=row["telegram_id"],
            company_name=row["company_name"],
            status=row["status"] or STATUS_APPROVED,
            username=col("username"),
            full_name=col("full_name"),
            schedule_days=col("schedule_days"),
            last_price_at=col("last_price_at"),
            last_reminder_at=col("last_reminder_at"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _select_sql(self) -> str:
        return (
            "SELECT telegram_id, company_name, status, username, full_name, "
            "schedule_days, last_price_at, last_reminder_at, created_at, updated_at "
            "FROM suppliers"
        )

    def get(self, telegram_id: int) -> Supplier | None:
        with self._connect() as conn:
            row = conn.execute(
                self._select_sql() + " WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_supplier(row)

    def get_approved(self, telegram_id: int) -> Supplier | None:
        supplier = self.get(telegram_id)
        if supplier is None or not supplier.is_approved:
            return None
        return supplier

    def list_approved_with_schedule(self) -> list[Supplier]:
        with self._connect() as conn:
            rows = conn.execute(
                self._select_sql()
                + " WHERE status = ? AND schedule_days IS NOT NULL AND schedule_days != ''",
                (STATUS_APPROVED,),
            ).fetchall()
        return [self._row_to_supplier(r) for r in rows]

    def list_all(self) -> list[Supplier]:
        with self._connect() as conn:
            rows = conn.execute(
                self._select_sql() + " ORDER BY company_name COLLATE NOCASE, telegram_id"
            ).fetchall()
        return [self._row_to_supplier(r) for r in rows]

    def bind(
        self,
        telegram_id: int,
        company_name: str,
        *,
        username: str | None = None,
        full_name: str | None = None,
        status: str = STATUS_APPROVED,
    ) -> Supplier:
        """Создать или сменить привязку user→компания (по умолчанию approved)."""
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT created_at, username, full_name FROM suppliers WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()
            created_at = existing["created_at"] if existing else now
            # Не затираем username/full_name, если новые не переданы
            keep_username = username if username is not None else (
                existing["username"] if existing else None
            )
            keep_full_name = full_name if full_name is not None else (
                existing["full_name"] if existing else None
            )
            conn.execute(
                """
                INSERT INTO suppliers (
                    telegram_id, company_name, status, username, full_name,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    company_name = excluded.company_name,
                    status = excluded.status,
                    username = COALESCE(excluded.username, suppliers.username),
                    full_name = COALESCE(excluded.full_name, suppliers.full_name),
                    updated_at = excluded.updated_at
                """,
                (
                    telegram_id,
                    company_name,
                    status,
                    keep_username,
                    keep_full_name,
                    created_at,
                    now,
                ),
            )
        return self.get(telegram_id)  # type: ignore[return-value]

    def unbind(self, telegram_id: int) -> bool:
        """Удалить привязку. True, если запись была."""
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM suppliers WHERE telegram_id = ?",
                (telegram_id,),
            )
            return cur.rowcount > 0

    def create_pending(
        self,
        telegram_id: int,
        company_name: str,
        username: str | None = None,
        full_name: str | None = None,
    ) -> Supplier:
        """Создать/обновить заявку со статусом pending (ждёт модерации)."""
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT created_at FROM suppliers WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()
            created_at = existing["created_at"] if existing else now
            conn.execute(
                """
                INSERT INTO suppliers (
                    telegram_id, company_name, status, username, full_name,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    company_name = excluded.company_name,
                    status = excluded.status,
                    username = excluded.username,
                    full_name = excluded.full_name,
                    updated_at = excluded.updated_at
                """,
                (
                    telegram_id,
                    company_name,
                    STATUS_PENDING,
                    username,
                    full_name,
                    created_at,
                    now,
                ),
            )
        return self.get(telegram_id)  # type: ignore[return-value]

    def set_status(self, telegram_id: int, status: str) -> Supplier | None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "UPDATE suppliers SET status = ?, updated_at = ? WHERE telegram_id = ?",
                (status, now, telegram_id),
            )
        return self.get(telegram_id)

    def approve(self, telegram_id: int) -> Supplier | None:
        return self.set_status(telegram_id, STATUS_APPROVED)

    def reject(self, telegram_id: int) -> Supplier | None:
        return self.set_status(telegram_id, STATUS_REJECTED)

    def set_schedule(self, telegram_id: int, days: set[int] | frozenset[int]) -> Supplier | None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        encoded = encode_schedule_days(days)
        with self._connect() as conn:
            conn.execute(
                "UPDATE suppliers SET schedule_days = ?, updated_at = ? WHERE telegram_id = ?",
                (encoded, now, telegram_id),
            )
        return self.get(telegram_id)

    def mark_price_sent(self, telegram_id: int, when: datetime | None = None) -> None:
        moment = (when or datetime.now(timezone.utc)).astimezone(timezone.utc)
        now = moment.isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "UPDATE suppliers SET last_price_at = ?, updated_at = ? WHERE telegram_id = ?",
                (now, now, telegram_id),
            )

    def mark_reminded(self, telegram_id: int, when: datetime | None = None) -> None:
        moment = (when or datetime.now(timezone.utc)).astimezone(timezone.utc)
        stamp = moment.isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "UPDATE suppliers SET last_reminder_at = ? WHERE telegram_id = ?",
                (stamp, telegram_id),
            )
