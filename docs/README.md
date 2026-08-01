# Freelancer Auto-Bidder

Автономный AI-агент для мониторинга и авто-биддинга заказов на Freelancer.com с Telegram-отчётностью.

## ⚠️ Важное предупреждение

Автоматизированная массовая отправка ставок и генерация откликов через ИИ может нарушать
[Условия использования Freelancer.com](https://www.freelancer.com/about/terms). Используйте на свой риск —
возможна блокировка аккаунта. Рекомендуется свериться с актуальной документацией
developers.freelancer.com и юридическими требованиями площадки перед продакшн-использованием.

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и заполните все переменные:
   ```bash
   cp .env.example .env
   ```

2. Запустите через Docker Compose (Postgres + Redis + бот, миграции применяются автоматически):
   ```bash
   docker compose up -d --build
   ```

3. Проверьте статус:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/metrics
   ```

## Локальный запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python main.py
```

## Команды бота

- `/start`, `/help` — доступны всем пользователям.
- `/stats`, `/report` — сводка по всем авто-ставкам. **Доступна только `CREATOR_ID`.**

## Архитектура

```
config/       — pydantic-settings конфигурация
database/     — ORM-модели, сессии, Unit of Work
schemas/      — Pydantic DTO для передачи данных между слоями
filters/      — include/exclude фильтр заказов, фильтр доступа creator-only
services/     — бизнес-логика: Gemini, Freelancer API, учёт ставок, оркестратор
handlers/     — Telegram-роутеры (creator.py — эксклюзив CREATOR_ID)
middlewares/  — throttling (Redis) и глобальный обработчик ошибок
src/          — фабрика бота/диспетчера, FastAPI приложение (/health, /metrics, webhook)
alembic/      — миграции БД
tests/        — юнит-тесты
```

## Переключение Polling / Webhook

В `.env`: `USE_WEBHOOK=false` — long polling (по умолчанию), `USE_WEBHOOK=true` — FastAPI webhook
по адресу `${WEBHOOK_HOST}${WEBHOOK_PATH}`.
