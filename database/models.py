"""
ORM-модели проекта.

Project  — заказы Freelancer.com, увиденные ботом (для дедупликации).
Bid      — успешно отправленные ставки, с автоинкрементным bid_number (Bid #1, #2...).
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import BigInteger, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Project(Base):
    """Заказ Freelancer.com, зафиксированный ботом (используется для дедупликации по external_id)."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    seen_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Project id={self.id} external_id={self.external_id!r}>"


class Bid(Base):
    """Успешно отправленная авто-ставка с порядковым номером (Bid #N)."""

    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bid_number: Mapped[int] = mapped_column(nullable=False, unique=True, index=True)

    project_external_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    project_title: Mapped[str] = mapped_column(String(512), nullable=False)
    project_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    bid_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_days: Mapped[int] = mapped_column(nullable=False)
    proposal_text: Mapped[str] = mapped_column(Text, nullable=False)

    freelancer_bid_id: Mapped[str] = mapped_column(String(64), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Bid #{self.bid_number} amount={self.bid_amount}>"
