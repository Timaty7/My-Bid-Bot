"""Rate limiter на Redis: защищает бота от флуда команд одним пользователем."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from redis.asyncio import Redis

from utils.logger import get_logger

log = get_logger(context="throttling")


class ThrottlingMiddleware(BaseMiddleware):
    """Ограничивает частоту обработки апдейтов от одного пользователя через Redis TTL-ключи."""

    def __init__(self, redis: Redis, rate_limit_seconds: float = 1.0) -> None:
        self._redis = redis
        self._rate_limit = rate_limit_seconds

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        key = f"throttle:{user.id}"
        is_allowed = await self._redis.set(key, "1", nx=True, ex=self._rate_limit)

        if not is_allowed:
            log.warning(f"Throttling: пользователь {user.id} превысил лимит частоты запросов")
            return None

        return await handler(event, data)
