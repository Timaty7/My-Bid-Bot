"""Фильтр aiogram, пропускающий только сообщения от CREATOR_ID."""
from __future__ import annotations

from aiogram.filters import Filter
from aiogram.types import Message

from config.settings import settings


class IsCreatorFilter(Filter):
    """True, если сообщение отправлено создателем бота (эксклюзивный доступ)."""

    async def __call__(self, message: Message) -> bool:
        return message.from_user is not None and message.from_user.id == settings.CREATOR_ID
