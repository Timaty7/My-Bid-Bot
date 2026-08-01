"""
Оркестратор Auto-Bidder: фоновый asyncio-цикл, который:
1. Раз в CHECK_INTERVAL секунд опрашивает ленту заказов Freelancer.com.
2. Отбрасывает уже виденные и не прошедшие include/exclude фильтр.
3. Отправляет прошедшие фильтр заказы в Gemini на анализ.
4. При положительном решении — сразу делает ставку через Freelancer API.
5. Молча (без сообщений в Telegram) сохраняет результат в БД с порядковым номером.
6. Уважает суточный лимит MAX_DAILY_BIDS.

Отчёт пользователю отдаётся только по команде /stats (handlers/user.py).
"""
from __future__ import annotations

import asyncio

import aiohttp

from config.settings import settings
from filters.project_filter import project_passes_filter
from schemas.bid import BidCreateDTO
from services.bid_service import BidService
from services.freelancer_service import FreelancerService
from services.gemini_service import GeminiService
from utils.logger import get_logger

log = get_logger(context="auto_bidder")


class AutoBidderService:
    """Фоновый воркер авто-биддинга. Запускается как asyncio.Task на старте приложения."""

    def __init__(self) -> None:
        self._gemini = GeminiService()
        self._bids = BidService()
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        """Сигнализирует воркеру завершить текущую итерацию и остановиться (graceful shutdown)."""
        self._stop_event.set()

    async def run_forever(self) -> None:
        """Основной бесконечный цикл мониторинга. Не падает при единичных сбоях итераций."""
        log.info("Auto-Bidder запущен")
        async with aiohttp.ClientSession() as http_session:
            freelancer = FreelancerService(http_session)
            while not self._stop_event.is_set():
                try:
                    await self._run_iteration(freelancer)
                except Exception as exc:  # noqa: BLE001 — итерация не должна валить весь цикл
                    log.error(f"Необработанная ошибка в итерации Auto-Bidder: {exc}")

                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=settings.CHECK_INTERVAL)
                except asyncio.TimeoutError:
                    pass
        log.info("Auto-Bidder остановлен")

    async def _run_iteration(self, freelancer: FreelancerService) -> None:
        bids_today = await self._bids.count_bids_today()
        if bids_today >= settings.MAX_DAILY_BIDS:
            log.info(f"Достигнут суточный лимит ставок ({bids_today}/{settings.MAX_DAILY_BIDS}), пропуск итерации")
            return

        projects = await freelancer.fetch_active_projects(settings.include_words_list)
        log.info(f"Получено {len(projects)} заказов из ленты Freelancer")

        for project in projects:
            if bids_today >= settings.MAX_DAILY_BIDS:
                log.info("Суточный лимит ставок достигнут в процессе итерации, останавливаемся")
                break

            if await self._bids.is_project_seen(project.external_id):
                continue

            await self._bids.mark_project_seen(project.external_id, project.title, project.url)

            if not project_passes_filter(project):
                continue

            decision = await self._gemini.evaluate_project(project)
            if not decision.should_bid:
                log.info(f"Gemini: SKIP_PROJECT для {project.external_id} ({project.title[:60]})")
                continue

            assert decision.bid_amount is not None
            assert decision.delivery_days is not None
            assert decision.proposal_text is not None

            freelancer_bid_id = await freelancer.submit_bid(
                project_external_id=project.external_id,
                bidder_id=settings.CREATOR_ID,
                amount=decision.bid_amount,
                period=decision.delivery_days,
                description=decision.proposal_text,
            )

            if freelancer_bid_id is None:
                log.error(f"Ставка НЕ отправлена (ошибка API) по проекту {project.external_id}")
                continue

            bid_number = await self._bids.save_bid(
                BidCreateDTO(
                    project_external_id=project.external_id,
                    project_title=project.title,
                    project_url=project.url,
                    bid_amount=decision.bid_amount,
                    delivery_days=decision.delivery_days,
                    proposal_text=decision.proposal_text,
                    freelancer_bid_id=freelancer_bid_id,
                )
            )
            bids_today += 1
            log.info(f"✅ Bid #{bid_number} отправлен по проекту '{project.title[:60]}' на сумму {decision.bid_amount}")
