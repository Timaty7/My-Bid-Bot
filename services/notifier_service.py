"""Сервис отправки служебных уведомлений создателю бота (startup/shutdown/critical errors)."""
from __future__ import annotations

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from config.settings import settings
from utils.logger import get_logger

log = get_logger(context="notifier")


class NotifierService:
    """Отправляет системные уведомления CREATOR_ID."""

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def notify_startup(self) -> None:
        await self._safe_send("🟢 Бот запущен и начал мониторинг заказов Freelancer.com.")

    async def notify_shutdown(self) -> None:
        await self._safe_send("🔴 Бот остановлен (graceful shutdown).")

    async def notify_critical(self, text: str) -> None:
        await self._safe_send(f"🚨 <b>CRITICAL ERROR</b>\n\n{text}")

    async def _safe_send(self, text: str) -> None:
        try:
            await self._bot.send_message(chat_id=settings.CREATOR_ID, text=text, parse_mode="HTML")
        except TelegramAPIError as exc:
            log.error(f"Не удалось отправить уведомление создателю: {exc}")
