"""
Сервис учёта ставок и проектов.

Отвечает за:
- дедупликацию проектов (чтобы не анализировать/не бидить один и тот же заказ дважды);
- атомарное сохранение ставки с присвоением следующего порядкового bid_number;
- подсчёт ставок за текущие сутки (для MAX_DAILY_BIDS);
- выборку всех ставок для команды /stats.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select

from database.models import Bid, Project
from database.uow import UnitOfWork
from schemas.bid import BidCreateDTO, BidReadDTO
from utils.logger import get_logger

log = get_logger(context="bid_service")


class BidService:
    """Сервисный слой для работы с проектами и ставками через Unit of Work."""

    async def is_project_seen(self, external_id: str) -> bool:
        """Проверяет, был ли проект уже обработан ранее (дедупликация)."""
        async with UnitOfWork() as uow:
            result = await uow.session.execute(
                select(Project.id).where(Project.external_id == external_id)
            )
            return result.scalar_one_or_none() is not None

    async def mark_project_seen(self, external_id: str, title: str, url: str) -> None:
        """Фиксирует проект как увиденный (вызывается сразу после первого анализа)."""
        async with UnitOfWork() as uow:
            uow.session.add(Project(external_id=external_id, title=title, url=url))

    async def count_bids_today(self) -> int:
        """Возвращает количество ставок, сделанных за сегодня (для лимита MAX_DAILY_BIDS)."""
        start_of_day = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        async with UnitOfWork() as uow:
            result = await uow.session.execute(
                select(func.count(Bid.id)).where(Bid.created_at >= start_of_day)
            )
            return result.scalar_one()

    async def save_bid(self, dto: BidCreateDTO) -> int:
        """
        Атомарно сохраняет ставку с автоматическим порядковым номером (Bid #N).
        Номер вычисляется как MAX(bid_number) + 1 в рамках той же транзакции.
        """
        async with UnitOfWork() as uow:
            result = await uow.session.execute(select(func.max(Bid.bid_number)))
            last_number = result.scalar_one_or_none() or 0
            next_number = last_number + 1

            bid = Bid(
                bid_number=next_number,
                project_external_id=dto.project_external_id,
                project_title=dto.project_title,
                project_url=dto.project_url,
                bid_amount=dto.bid_amount,
                delivery_days=dto.delivery_days,
                proposal_text=dto.proposal_text,
                freelancer_bid_id=dto.freelancer_bid_id,
            )
            uow.session.add(bid)
            await uow.session.flush()
            log.info(f"Сохранена ставка Bid #{next_number} по проекту {dto.project_external_id}")
            return next_number

    async def get_all_bids(self) -> list[BidReadDTO]:
        """Возвращает все ставки в хронологическом порядке для отчёта /stats."""
        async with UnitOfWork() as uow:
            result = await uow.session.execute(select(Bid).order_by(Bid.bid_number.asc()))
            bids = result.scalars().all()
            return [BidReadDTO.model_validate(b) for b in bids]
