"""
Роутер, эксклюзивный для CREATOR_ID.

Команды:
- /stats, /report — сводка по всем авто-ставкам, сделанным ботом.
"""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from filters.is_creator import IsCreatorFilter
from schemas.bid import BidReadDTO
from services.bid_service import BidService
from utils.logger import get_logger

router = Router(name="creator")
router.message.filter(IsCreatorFilter())

log = get_logger(context="creator_handler")

_TELEGRAM_MESSAGE_LIMIT = 4000


@router.message(Command("stats", "report"))
async def cmd_stats(message: Message) -> None:
    """Отправляет создателю структурированную сводку по всем сделанным авто-ставкам."""
    log.info(f"Создатель {message.from_user.id} запросил отчёт /stats")

    bid_service = BidService()
    bids = await bid_service.get_all_bids()

    if not bids:
        await message.answer("📊 Сводка авто-ставок:\n\nПока нет ни одной отправленной ставки.")
        return

    for chunk in _format_report(bids):
        await message.answer(chunk, disable_web_page_preview=True)


def _format_report(bids: list[BidReadDTO]) -> list[str]:
    """Форматирует список ставок в отчёт, разбивая на части по лимиту длины сообщения Telegram."""
    header = "📊 Сводка авто-ставок:\n"
    chunks: list[str] = []
    current = header

    for bid in bids:
        entry = (
            f"\n🔹 Bid #{bid.bid_number}\n"
            f"- Проект: {bid.project_title} (${bid.bid_amount:.0f})\n"
            f"- Ссылка: {bid.project_url}\n"
            f"- Время: {bid.created_at.strftime('%H:%M %d.%m.%Y')}\n"
        )
        if len(current) + len(entry) > _TELEGRAM_MESSAGE_LIMIT:
            chunks.append(current)
            current = entry
        else:
            current += entry

    chunks.append(current)
    return chunks
