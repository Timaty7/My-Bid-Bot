"""Глобальный перехватчик исключений: логирует traceback и шлёт CRITICAL-алерты создателю."""
from __future__ import annotations

import traceback
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from services.notifier_service import NotifierService
from utils.logger import get_logger

log = get_logger(context="error_handler")


class GlobalErrorMiddleware(BaseMiddleware):
    """Ловит все необработанные исключения в handlers, логирует и уведомляет создателя."""

    def __init__(self, notifier: NotifierService) -> None:
        self._notifier = notifier

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as exc:  # noqa: BLE001 — намеренно широкий перехват на верхнем уровне
            tb = traceback.format_exc()
            log.error(f"Необработанное исключение в handler'е: {exc}\n{tb}")
            await self._notifier.notify_critical(f"<pre>{tb[-3500:]}</pre>")
            return None
