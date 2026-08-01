"""
FastAPI-приложение.

Предоставляет:
- /health   — проверка живости для docker healthcheck / оркестратора;
- /metrics  — базовые метрики авто-биддера (кол-во ставок сегодня, всего, аптайм);
- webhook   — приём апдейтов Telegram, если USE_WEBHOOK=true.

Также отвечает за полный жизненный цикл процесса: старт/стоп фонового Auto-Bidder,
graceful shutdown соединений с БД/Redis, авто-уведомления создателю.
"""
from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager

from aiogram.types import Update
from aiogram.webhook.aiohttp_server import setup_application  # noqa: F401 — оставлено для webhook-server сценария на aiohttp, не используется напрямую в FastAPI-варианте
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from redis.asyncio import Redis

from config.settings import settings
from database.session import dispose_engine, engine
from services.auto_bidder_service import AutoBidderService
from services.bid_service import BidService
from src.bot_factory import create_bot, create_dispatcher
from utils.logger import get_logger, setup_logger

log = get_logger(context="app")

_start_time = time.monotonic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет полным жизненным циклом: инициализация -> работа -> graceful shutdown."""
    setup_logger()
    log.info("Инициализация приложения...")

    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    bot = create_bot()
    dp = create_dispatcher(bot, redis)

    app.state.bot = bot
    app.state.dp = dp
    app.state.redis = redis

    notifier = dp["notifier"]
    auto_bidder = AutoBidderService()
    app.state.auto_bidder = auto_bidder

    bidder_task = asyncio.create_task(auto_bidder.run_forever(), name="auto_bidder")

    if settings.USE_WEBHOOK:
        await bot.set_webhook(
            url=f"{settings.WEBHOOK_HOST}{settings.WEBHOOK_PATH}",
            secret_token=settings.WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        log.info("Бот запущен в режиме Webhook")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        polling_task = asyncio.create_task(dp.start_polling(bot), name="polling")
        app.state.polling_task = polling_task
        log.info("Бот запущен в режиме Long Polling")

    await notifier.notify_startup()

    yield

    # ---- Graceful shutdown ----
    log.info("Остановка приложения...")
    await notifier.notify_shutdown()

    auto_bidder.stop()
    bidder_task.cancel()

    if not settings.USE_WEBHOOK and hasattr(app.state, "polling_task"):
        app.state.polling_task.cancel()
        await dp.stop_polling()

    await bot.session.close()
    await redis.aclose()
    await dispose_engine()
    log.info("Приложение остановлено, все ресурсы освобождены")


app = FastAPI(title="Freelancer Auto-Bidder", lifespan=lifespan)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    """Проверка живости приложения (для docker-compose healthcheck)."""
    try:
        async with engine.connect():
            pass
    except Exception as exc:  # noqa: BLE001
        log.error(f"Health check: БД недоступна: {exc}")
        raise HTTPException(status_code=503, detail="database unavailable") from exc

    try:
        await app.state.redis.ping()
    except Exception as exc:  # noqa: BLE001
        log.error(f"Health check: Redis недоступен: {exc}")
        raise HTTPException(status_code=503, detail="redis unavailable") from exc

    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> dict[str, float | int]:
    """Базовые метрики приложения."""
    bid_service = BidService()
    bids_today = await bid_service.count_bids_today()
    all_bids = await bid_service.get_all_bids()

    return {
        "uptime_seconds": round(time.monotonic() - _start_time, 1),
        "bids_today": bids_today,
        "bids_total": len(all_bids),
        "max_daily_bids": settings.MAX_DAILY_BIDS,
    }


@app.post(settings.WEBHOOK_PATH)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> Response:
    """Приём апдейтов Telegram в режиме Webhook. Проверяет секретный токен."""
    if not settings.USE_WEBHOOK:
        raise HTTPException(status_code=404, detail="webhook disabled")

    if x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="invalid secret token")

    data = await request.json()
    update = Update.model_validate(data, context={"bot": request.app.state.bot})
    await request.app.state.dp.feed_update(request.app.state.bot, update)
    return Response(status_code=200)
