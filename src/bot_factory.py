"""Фабрика создания Bot/Dispatcher aiogram с подключёнными middlewares и роутерами."""
from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from redis.asyncio import Redis

from config.settings import settings
from handlers import creator, user
from middlewares.error_handler import GlobalErrorMiddleware
from middlewares.throttling import ThrottlingMiddleware
from services.notifier_service import NotifierService


def create_bot() -> Bot:
    """Создаёт экземпляр Bot с настройками по умолчанию (HTML parse mode)."""
    return Bot(
        token=settings.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(bot: Bot, redis: Redis) -> Dispatcher:
    """Создаёт Dispatcher, регистрирует middlewares и роутеры."""
    dp = Dispatcher()

    notifier = NotifierService(bot)

    dp.update.outer_middleware(GlobalErrorMiddleware(notifier))
    dp.update.outer_middleware(ThrottlingMiddleware(redis, rate_limit_seconds=1.0))

    dp.include_router(creator.router)
    dp.include_router(user.router)

    dp["notifier"] = notifier
    return dp
