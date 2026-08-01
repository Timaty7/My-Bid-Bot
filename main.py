"""
Единая точка входа приложения.

Поднимает FastAPI-приложение (src/app.py) через uvicorn. Внутри lifespan
FastAPI-приложения запускается aiogram-бот (polling или webhook — по .env)
и фоновый Auto-Bidder воркер.
"""
from __future__ import annotations

import uvicorn

from config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=settings.WEBAPP_HOST,
        port=settings.WEBAPP_PORT,
        log_config=None,  # логирование полностью на loguru, см. utils/logger.py
    )
