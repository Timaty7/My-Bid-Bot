"""DTO-схемы, связанные со ставками."""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


class BidCreateDTO(BaseModel):
    """Данные для создания записи о ставке в БД (Handlers/Services -> DB строго через DTO)."""

    model_config = ConfigDict(frozen=True)

    project_external_id: str
    project_title: str
    project_url: str
    bid_amount: float
    delivery_days: int
    proposal_text: str
    freelancer_bid_id: str | None = None


class BidReadDTO(BaseModel):
    """Представление ставки для отчёта /stats."""

    model_config = ConfigDict(from_attributes=True)

    bid_number: int
    project_title: str
    project_url: str
    bid_amount: float
    created_at: dt.datetime
