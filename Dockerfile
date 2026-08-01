FROM python:3.11-slim

# Системные зависимости для сборки asyncpg/uvloop и т.п.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Непривилегированный пользователь
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Применяем миграции и запускаем приложение
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
