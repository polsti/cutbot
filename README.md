# cutbot

Telegram bot for calorie/macro tracking, fasting, cut/bulk — see the product spec (ТЗ) for full scope.

## Stack
- Python 3.12+, [aiogram 3](https://docs.aiogram.dev/) (polling mode)
- PostgreSQL (Supabase), SQLAlchemy 2.0 (async), Alembic migrations
- APScheduler for reminders

## Local setup
1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and fill in `BOT_TOKEN` (from [@BotFather](https://t.me/BotFather)) and `DATABASE_URL` (from your Supabase project)
4. `alembic upgrade head`
5. `python -m bot.main`

## Branching
One branch per build phase (`phase-N-<name>`), merged into `main` once that phase runs end-to-end.

## Docker
```
docker build -t cutbot .
docker run --env-file .env cutbot
```
