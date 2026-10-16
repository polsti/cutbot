"""add voice column to users

Revision ID: e39dcf06b342
Revises: f18a17bbb735
Create Date: 2026-10-16 15:12:15.609295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e39dcf06b342'
down_revision: Union[str, None] = 'f18a17bbb735'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("voice", sa.String(length=20), nullable=False, server_default="smaev"))
    op.alter_column("users", "voice", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "voice")
