"""DTO-схемы, связанные с заказами Freelancer.com."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProjectDTO(BaseModel):
    """Заказ, полученный от Freelancer API (сырые данные ленты)."""

    model_config = ConfigDict(frozen=True)

    external_id: str = Field(..., description="ID проекта на Freelancer.com")
    title: str
    description: str
    url: str
    currency: str = "USD"
    min_budget: float | None = None
    max_budget: float | None = None


class AIBidDecisionDTO(BaseModel):
    """Ответ Gemini по конкретному проекту: либо SKIP, либо параметры ставки."""

    model_config = ConfigDict(frozen=True)

    should_bid: bool
    bid_amount: float | None = None
    delivery_days: int | None = None
    proposal_text: str | None = None
