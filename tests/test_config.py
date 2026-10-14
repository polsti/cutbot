import os

os.environ.setdefault("BOT_TOKEN", "dummy")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/dbname")

from bot.config import settings  # noqa: E402
from bot.models.base import Base  # noqa: E402
from bot.models.user import User  # noqa: E402


def test_settings_loaded():
    assert settings.bot_token == "dummy"
    assert "postgresql" in settings.database_url


def test_user_table_registered():
    assert "users" in Base.metadata.tables
