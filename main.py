from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from src.config import load_config
from src.handlers import setup_routers
from src.middlewares import DependenciesMiddleware
from src.services.reminders import send_due_reminders
from src.services.suppliers import SupplierRepo
from src.timeutil import YAKUTSK

logger = logging.getLogger(__name__)


async def main() -> None:
    load_dotenv()
    config = load_config()

    # MemoryStorage: FSM-состояния только в RAM (после рестарта «шаг диалога» сбросится).
    # Привязка user→компания живёт в SQLite (SupplierRepo) — она переживает рестарт.
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    suppliers = SupplierRepo(config.data_dir / "suppliers.db")
    deps = DependenciesMiddleware(config, suppliers)
    # outer — до фильтров; и message, и callback_query получат config/suppliers
    dp.update.middleware(deps)

    dp.include_router(setup_routers())

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    scheduler = AsyncIOScheduler(timezone=YAKUTSK)

    async def reminder_job() -> None:
        count = await send_due_reminders(bot, suppliers)
        if count:
            logger.info("Price reminders sent: %s", count)

    for hour in config.reminder_hours:
        scheduler.add_job(
            reminder_job,
            CronTrigger(hour=hour, minute=0, timezone=YAKUTSK),
            id=f"price_reminder_{hour}",
            replace_existing=True,
        )
    scheduler.start()
    logger.info(
        "Reminder scheduler started (Yakutsk hours=%s)",
        config.reminder_hours,
    )

    try:
        # drop_pending_updates=True: не разгребать очередь, накопившуюся пока бот был выключен
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
