"""
Сервис интеграции с Freelancer.com API.

Отвечает за:
- получение ленты новых активных проектов;
- отправку ставки (POST) по решению ИИ.

ВАЖНО: конкретные пути/параметры REST API Freelancer.com (endpoints, поля ответа)
нужно свериться с официальной документацией developers.freelancer.com — структура
запросов ниже реализует стандартный паттерн Freelancer API v1 (Oauth2 Bearer token,
/api/projects/0.1/projects/active/, /api/projects/0.1/projects/{id}/bids/).
"""
from __future__ import annotations

from typing import Any

import aiohttp

from config.settings import settings
from schemas.project import ProjectDTO
from utils.logger import get_logger

log = get_logger(context="freelancer_service")


class FreelancerAPIError(Exception):
    """Ошибка взаимодействия с Freelancer API."""


class FreelancerService:
    """Клиент Freelancer.com API поверх aiohttp.ClientSession."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._base_url = settings.FREELANCER_API_URL.rstrip("/")
        self._headers = {
            "Freelancer-OAuth-V1": settings.FREELANCER_ACCESS_TOKEN,
            "Content-Type": "application/json",
        }

    async def fetch_active_projects(self, query_words: list[str]) -> list[ProjectDTO]:
        """Запрашивает ленту активных проектов по ключевым словам."""
        params = {
            "query": " ".join(query_words),
            "limit": 50,
            "compact": "true",
            "full_description": "true",
        }
        url = f"{self._base_url}/projects/0.1/projects/active/"

        try:
            async with self._session.get(url, headers=self._headers, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise FreelancerAPIError(f"Freelancer API вернул статус {resp.status}: {body[:300]}")
                payload = await resp.json()
        except aiohttp.ClientError as exc:
            log.error(f"Сетевая ошибка при получении ленты заказов: {exc}")
            return []
        except FreelancerAPIError as exc:
            log.error(str(exc))
            return []

        raw_projects = payload.get("result", {}).get("projects", [])
        return [self._to_dto(item) for item in raw_projects if item]

    async def submit_bid(
        self,
        project_external_id: str,
        bidder_id: int,
        amount: float,
        period: int,
        description: str,
    ) -> str | None:
        """
        Отправляет ставку по проекту. Возвращает ID созданной ставки на Freelancer или None при ошибке.
        """
        url = f"{self._base_url}/projects/0.1/bids/"
        body: dict[str, Any] = {
            "project_id": project_external_id,
            "bidder_id": bidder_id,
            "amount": amount,
            "period": period,
            "description": description,
        }

        try:
            async with self._session.post(url, headers=self._headers, json=body, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status not in (200, 201):
                    err_body = await resp.text()
                    log.error(f"Не удалось отправить ставку по проекту {project_external_id}: {resp.status} {err_body[:300]}")
                    return None
                payload = await resp.json()
                bid_id = str(payload.get("result", {}).get("id", ""))
                log.info(f"Ставка успешно отправлена по проекту {project_external_id}, freelancer_bid_id={bid_id}")
                return bid_id or None
        except aiohttp.ClientError as exc:
            log.error(f"Сетевая ошибка при отправке ставки по проекту {project_external_id}: {exc}")
            return None

    @staticmethod
    def _to_dto(raw: dict[str, Any]) -> ProjectDTO:
        budget = raw.get("budget", {}) or {}
        return ProjectDTO(
            external_id=str(raw.get("id")),
            title=raw.get("title", ""),
            description=raw.get("preview_description") or raw.get("description", ""),
            url=f"https://www.freelancer.com/projects/{raw.get('seo_url', raw.get('id'))}",
            currency=(raw.get("currency", {}) or {}).get("code", "USD"),
            min_budget=budget.get("minimum"),
            max_budget=budget.get("maximum"),
        )
