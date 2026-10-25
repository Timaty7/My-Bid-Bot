# My Bid Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

<p align="center">
  <a href="https://github.com/timatym1/My-Bid-Bot/actions"><img src="https://img.shields.io/github/actions/workflow/status/timatym1/My-Bid-Bot/ci.yml?branch=main&label=CI" alt="CI status" /></a>
  <a href="https://github.com/timatym1/My-Bid-Bot"><img src="https://img.shields.io/github/stars/timatym1/My-Bid-Bot?style=social" alt="GitHub stars" /></a>
  <a href="https://github.com/timatym1/My-Bid-Bot/issues"><img src="https://img.shields.io/github/issues/timatym1/My-Bid-Bot" alt="Issues" /></a>
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=24&pause=1000&color=5EEAD4&center=true&vCenter=true&width=700&lines=Freelancer+Auto-Bidder;AI-powered+job+filtering;Telegram+monitoring+and+alerts" alt="My Bid Bot banner" />
</p>

<div align="center">
  <h3>🚀 AI-powered Freelancer bidding assistant</h3>
  <p>
    Monitor job posts, filter the best opportunities, trigger smart bids, and get real-time Telegram updates — all from one automated workflow.
  </p>
</div>

## ✨ Why this project?

My Bid Bot is a fully automated freelance monitoring system built for Freelancer.com workflows. It watches incoming job posts, filters them using your preferences, evaluates whether the project matches your target profile, and can automatically prepare and submit bids with AI-driven reasoning.

The bot keeps you informed through Telegram notifications and exposes health/metrics endpoints for lightweight operational monitoring.

## 🎯 Core features

<div align="center">

| Feature | Description |
| --- | --- |
| 🤖 AI bid assistant | Uses Gemini models to evaluate opportunities and generate bidding strategy guidance |
| 🔎 Smart filtering | Include/exclude keywords and custom job targeting rules |
| 📡 Telegram monitoring | Sends startup, shutdown, stats and alerts directly to a Telegram chat |
| 🧠 Auto-bid workflow | Scans jobs on a schedule and manages daily bid limits |
| 🗄️ Persistent storage | PostgreSQL for structured records, Redis for throttling and queue-like operations |
| ⚙️ Docker-ready | Run the bot, database and Redis together in a single stack |
| 📈 Health checks | FastAPI endpoints for `/health` and `/metrics` |
| 🔐 Webhook or polling | Flexible Telegram deployment mode with secure webhook validation |

</div>

## 🧩 How it works

1. The bot fetches available Freelancer jobs and inspects their titles/descriptions.
2. Filter rules decide whether a project is relevant or should be ignored.
3. Gemini AI analyzes the opportunity, helps create a fitting bid strategy, and prepares the response.
4. The system checks configured daily limits and submits or schedules bids accordingly.
5. Telegram sends actionable updates and summary reports to the creator account.

## 📸 Demo / preview

> A quick marketing-style mockup of the workflow.

```text
┌──────────────────────────────────────────────────────────────┐
│ Freelancer.com                                              │
│  ├─ New project matched: "Python Telegram bot automation"  │
│  ├─ Score: 94/100                                            │
│  ├─ Keywords: python, api, automation, bot                  │
│  └─ AI reasoning: strong fit for backend automation         │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ My Bid Bot                                                  │
│  ✓ Filtered by include/exclude rules                        │
│  ✓ Gemini evaluation completed                              │
│  ✓ Daily bid quota checked                                  │
│  ✓ Telegram alert sent to creator                           │
└──────────────────────────────────────────────────────────────┘
```

### Example Telegram notification

```text
📣 New qualified job detected

Project: Python automation bot for client onboarding
Category: Bot Development / API Integration
Fit score: 94%
AI summary: This is a strong match for Python automation work and API integration.

Bid status: prepared and queued
```

## 🚀 Quick start

### 1) Clone the repository

```bash
git clone https://github.com/timatym1/My-Bid-Bot.git
cd My-Bid-Bot
```

### 2) Configure environment variables

```bash
cp .env.example .env
```

Then edit the file and fill in your values for:

- Telegram token and chat IDs
- Gemini API keys
- Freelancer API token
- PostgreSQL credentials
- Redis credentials
- webhook settings if using webhooks

### 3) Start with Docker Compose

```bash
docker compose up -d --build
```

### 4) Health and monitoring

```bash
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

## 🐳 Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python main.py
```

## ⚙️ Environment configuration

The application reads settings from `.env` through `config/settings.py`.

### Required variables

```dotenv
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CREATOR_ID=your_telegram_user_id_here
GEMINI_API_KEYS=key1,key2,key3
FREELANCER_ACCESS_TOKEN=your_freelancer_oauth_token
POSTGRES_USER=freelancer_bot
POSTGRES_PASSWORD=change_me_strong_password
POSTGRES_DB=freelancer_bot
REDIS_PASSWORD=change_me_redis_password
WEBHOOK_SECRET=change_me_to_a_random_32_char_string
```

### Optional tuning

```dotenv
USE_WEBHOOK=false
WEBHOOK_HOST=https://your-domain.example.com
WEBHOOK_PATH=/webhook
CHECK_INTERVAL=60
MAX_DAILY_BIDS=20
INCLUDE_WORDS=python,bot,scrape,api,automation
EXCLUDE_WORDS=wordpress,php,java,c++,laravel,seo
```

## 🏗️ Project structure

```text
.
├── alembic/              # database migrations
├── config/               # pydantic settings and env config
├── database/             # ORM models and DB session setup
├── docs/                 # project docs and notes
├── filters/              # include/exclude job matching rules
├── handlers/             # Telegram command handlers
├── keyboards/            # Telegram keyboards and inline UI
├── middlewares/          # rate limiting and error handling
├── services/             # business logic: Gemini, Freelancer, bidding, orchestration
├── schemas/              # DTOs and data contracts
├── src/                  # FastAPI app and bot factory
├── states/               # bot state logic
├── tests/                # unit tests
├── utils/                # logging and helper utilities
├── .env.example          # example configuration
├── Dockerfile            # container image
├── docker-compose.yml    # local orchestration stack
├── main.py               # app entrypoint
├── requirements.txt      # Python dependencies
├── alembic.ini           # Alembic migration config
├── README.md             # project documentation
└── LICENSE               # project license (if present)
```

## 📡 Bot commands

- `/start` — initialize the bot
- `/help` — show available commands
- `/stats` — view auto-bid stats (creator-only)
- `/report` — send summary reports (creator-only)

## 🩺 Monitoring endpoints

The application exposes the following endpoints via FastAPI:

- `GET /health` — verifies database + Redis readiness
- `GET /metrics` — uptime, bids today, total bids, configured daily cap
- `POST /webhook` — Telegram webhook endpoint when `USE_WEBHOOK=true`

## 🔐 Important notice

This project automates job discovery and bidding workflows. Please review the platform's terms and regulations before using it in production.

Using automated mass-bidding or AI-generated proposals may violate platform policies or account terms. Use responsibly and only in compliance with the applicable Freelancer.com rules and local legal requirements.

## 🏁 Development roadmap

- Add richer job scoring and prioritization logic
- Expand bid-quality checks and reject heuristics
- Add analytics dashboard for performance reporting
- Improve retry logic and rate-limit resilience
- Add secure audit logs and bid history exports

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request with a clear summary

## 📜 License

This project is currently distributed under the repository license. Please check the project root for the exact license file before using it in production or redistributing it.

---

<p align="center">
  <b>Built for automated freelance workflows.</b>
</p>
