"""DI через middleware: кладём зависимости в handler data.

В aiogram 3 хендлер получает kwargs не только из update, но и из data,
которую наполняют middleware. Это и есть «внедрение зависимостей» без глобалов.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.config import Config
from src.services.suppliers import SupplierRepo


class DependenciesMiddleware(BaseMiddleware):
    def __init__(self, config: Config, suppliers: SupplierRepo) -> None:
        self._config = config
        self._suppliers = suppliers

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["config"] = self._config
        data["suppliers"] = self._suppliers
        return await handler(event, data)
