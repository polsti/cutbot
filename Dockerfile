FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bring the database schema up to date before the bot starts, so a deploy
# never runs new code against an old schema. If a migration fails, the
# bot doesn't start and the error shows in Render's logs.
CMD ["sh", "-c", "alembic upgrade head && python -m bot.main"]
