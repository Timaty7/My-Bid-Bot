"""
Unit of Work — обеспечивает атомарность транзакций между сервисным слоем и БД.
Используется как async context manager: под капотом commit/rollback гарантированы.
"""
from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from database.session import async_session_factory
from utils.logger import get_logger

log = get_logger(context="uow")


class UnitOfWork:
    """Атомарная единица работы с БД. Пример: async with UnitOfWork() as uow: ..."""

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self.session = async_session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert self.session is not None
        try:
            if exc_type is not None:
                await self.session.rollback()
                log.warning(f"Транзакция откачена из-за исключения: {exc_val}")
            else:
                await self.session.commit()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        assert self.session is not None
        await self.session.commit()

    async def rollback(self) -> None:
        assert self.session is not None
        await self.session.rollback()
