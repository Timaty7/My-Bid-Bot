"""
Сервис интеграции с Gemini API.

Anti-Limit System: при получении 429/quota exceeded от текущего ключа
сервис автоматически переключается на следующий ключ из списка GEMINI_API_KEYS
и повторяет запрос, не останавливая бота.
"""
from __future__ import annotations

import json
from itertools import cycle
from typing import Any

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, TooManyRequests

from config.settings import settings
from schemas.project import AIBidDecisionDTO, ProjectDTO
from utils.logger import get_logger

log = get_logger(context="gemini_service")

_SYSTEM_PROMPT = """\
Ты — эксперт по фрилансу и Python-разработке, помогаешь оценивать заказы на Freelancer.com \
для профиля разработчика, специализирующегося на Python, ботах, скрапинге, автоматизации и API-интеграциях \
(включая "Vibe Coding" — быструю разработку прототипов с помощью ИИ-инструментов).

Тебе передан заказ. Прими решение:

1. Если заказ — скам, требует другой стек (не Python), не относится к разработке ПО, \
или явно не подходит под профиль — верни JSON:
{"should_bid": false}

2. Если заказ подходит — верни JSON:
{
  "should_bid": true,
  "bid_amount": <число, идеальная конкурентная ставка в USD (sweet spot)>,
  "delivery_days": <целое число дней на выполнение>,
  "proposal_text": "<текст отклика на английском языке, до 1000 символов, БЕЗ штампов вроде \
'I am thrilled' / 'I am excited' / общих фраз, первые 2 строки — сильный конкретный hook по сути задачи>"
}

Отвечай СТРОГО валидным JSON без markdown-разметки, без пояснений вне JSON.
"""


class GeminiKeyRotator:
    """Циклический ротатор API-ключей Gemini."""

    def __init__(self, keys: list[str]) -> None:
        if not keys:
            raise ValueError("Список ключей Gemini пуст")
        self._keys = keys
        self._cycle = cycle(keys)
        self.current_key: str = next(self._cycle)

    def rotate(self) -> str:
        """Переключается на следующий ключ и возвращает его."""
        self.current_key = next(self._cycle)
        log.warning(f"Ротация ключа Gemini выполнена, новый ключ: ...{self.current_key[-4:]}")
        return self.current_key


class GeminiService:
    """Обёртка над Gemini API с авто-ротацией ключей при исчерпании лимита."""

    def __init__(self) -> None:
        self._rotator = GeminiKeyRotator(settings.gemini_keys_list)
        self._configure(self._rotator.current_key)

    @staticmethod
    def _configure(api_key: str) -> None:
        genai.configure(api_key=api_key)

    async def evaluate_project(self, project: ProjectDTO) -> AIBidDecisionDTO:
        """
        Отправляет проект на анализ Gemini и возвращает решение по ставке.
        При 429/quota exceeded — ротирует ключ и повторяет попытку (максимум N раз = кол-во ключей).
        """
        prompt = self._build_prompt(project)
        max_attempts = len(settings.gemini_keys_list)

        for attempt in range(1, max_attempts + 1):
            try:
                model = genai.GenerativeModel(
                    model_name=settings.GEMINI_MODEL,
                    system_instruction=_SYSTEM_PROMPT,
                )
                response = await model.generate_content_async(prompt)
                return self._parse_response(response.text)

            except (ResourceExhausted, TooManyRequests) as exc:
                log.warning(f"Лимит Gemini исчерпан (попытка {attempt}/{max_attempts}): {exc}")
                self._configure(self._rotator.rotate())
                continue

            except Exception as exc:  # noqa: BLE001 — сетевые сбои не должны валить бота
                # Отдельно ловим текстовые признаки лимита, если библиотека вернула generic-ошибку
                if "429" in str(exc) or "quota" in str(exc).lower():
                    log.warning(f"Лимит Gemini исчерпан (generic, попытка {attempt}/{max_attempts}): {exc}")
                    self._configure(self._rotator.rotate())
                    continue
                log.error(f"Ошибка запроса к Gemini для проекта {project.external_id}: {exc}")
                return AIBidDecisionDTO(should_bid=False)

        log.error(f"Все ключи Gemini исчерпаны для проекта {project.external_id}, пропуск")
        return AIBidDecisionDTO(should_bid=False)

    @staticmethod
    def _build_prompt(project: ProjectDTO) -> str:
        return (
            f"Заголовок: {project.title}\n"
            f"Описание: {project.description}\n"
            f"Бюджет: {project.min_budget}-{project.max_budget} {project.currency}\n"
        )

    @staticmethod
    def _parse_response(raw_text: str) -> AIBidDecisionDTO:
        """Парсит JSON-ответ Gemini, устойчиво к обрамлению markdown-кодблоками."""
        cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data: dict[str, Any] = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            log.error(f"Не удалось распарсить JSON от Gemini: {exc}. Сырой ответ: {raw_text[:200]}")
            return AIBidDecisionDTO(should_bid=False)

        if not data.get("should_bid"):
            return AIBidDecisionDTO(should_bid=False)

        return AIBidDecisionDTO(
            should_bid=True,
            bid_amount=data.get("bid_amount"),
            delivery_days=data.get("delivery_days"),
            proposal_text=data.get("proposal_text"),
        )
