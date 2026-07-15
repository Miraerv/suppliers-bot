"""Напоминания поставщикам: «сегодня день прайса, а файла ещё нет»."""

from __future__ import annotations

import logging
from datetime import datetime

from aiogram import Bot

from src import texts
from src.keyboards.common import known_user_keyboard
from src.services.suppliers import SupplierRepo
from src.timeutil import now_yakutsk, to_yakutsk

logger = logging.getLogger(__name__)

# Между двумя «пинкам» в один день (10:00 и 15:00) — минимум 4 часа
MIN_HOURS_BETWEEN_REMINDERS = 4


async def send_due_reminders(bot: Bot, suppliers: SupplierRepo) -> int:
    """Разослать напоминания тем, у кого сегодня день по календарю и нет прайса.

    В выбранный день можно несколько раз (по REMINDER_HOURS), но не чаще
    чем раз в MIN_HOURS_BETWEEN_REMINDERS часов. Если прайс уже сдан — молчим.
    """
    now = now_yakutsk()
    today = now.date()
    weekday = today.weekday()  # 0=Пн … 6=Вс
    sent = 0

    for supplier in suppliers.list_approved_with_schedule():
        if weekday not in supplier.weekdays:
            continue
        if supplier.price_sent_on(today):
            continue
        if supplier.last_reminder_at:
            try:
                last = to_yakutsk(datetime.fromisoformat(supplier.last_reminder_at))
                hours = (now - last).total_seconds() / 3600
                if hours < MIN_HOURS_BETWEEN_REMINDERS:
                    continue
            except ValueError:
                pass

        try:
            await bot.send_message(
                chat_id=supplier.telegram_id,
                text=texts.price_reminder(supplier.company_name),
                reply_markup=known_user_keyboard(),
            )
            suppliers.mark_reminded(supplier.telegram_id)
            sent += 1
            logger.info(
                "Reminder sent to telegram_id=%s company=%r",
                supplier.telegram_id,
                supplier.company_name,
            )
        except Exception:
            logger.exception(
                "Failed to send price reminder to telegram_id=%s",
                supplier.telegram_id,
            )

    return sent