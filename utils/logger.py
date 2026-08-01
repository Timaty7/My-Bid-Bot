"""
Настройка структурированного логирования через loguru.
Логи пишутся в консоль (для docker logs) и в файл logs/app.log с ротацией.
"""
from __future__ import annotations

import sys

from loguru import logger

from config.settings import settings


def setup_logger() -> None:
    """Инициализирует loguru: убирает дефолтный обработчик, добавляет консоль и файл."""
    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[context]}</cyan> | "
            "<level>{message}</level>"
        ),
        filter=_ensure_context,
    )

    logger.add(
        "logs/app.log",
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        encoding="utf-8",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[context]} | {message}"
        ),
        filter=_ensure_context,
    )


def _ensure_context(record: dict) -> bool:
    """Гарантирует наличие поля context, чтобы формат не падал при обычных logger.info()."""
    record["extra"].setdefault("context", "system")
    return True


def get_logger(**context: object):
    """
    Возвращает logger с привязанным контекстом (user_id, chat_id, handler и т.д.).
    Пример: log = get_logger(handler="creator", user_id=message.from_user.id)
    """
    ctx_str = " ".join(f"{k}={v}" for k, v in context.items()) or "system"
    return logger.bind(context=ctx_str)
