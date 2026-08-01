"""Базовые команды, доступные любому пользователю (не эксклюзив создателя)."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router(name="user")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привет! Это Auto-Bidder для Freelancer.com.\n"
        "Бот работает в фоне и автоматически анализирует и ставит на подходящие заказы.\n"
        "Сводка по ставкам доступна только создателю бота."
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — эта справка\n\n"
        "Отчёт по ставкам (/stats) доступен только создателю бота."
    )
