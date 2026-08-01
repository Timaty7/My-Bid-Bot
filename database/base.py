"""Базовый класс для всех ORM-моделей проекта."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый декларативный класс SQLAlchemy 2.0 для всех моделей."""
    pass
