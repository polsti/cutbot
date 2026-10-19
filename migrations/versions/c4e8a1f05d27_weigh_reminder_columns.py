"""weigh-in reminder columns on users

Revision ID: c4e8a1f05d27
Revises: b7c2d91e4f03
Create Date: 2026-10-19 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4e8a1f05d27'
down_revision: Union[str, None] = 'b7c2d91e4f03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("weigh_reminder", sa.String(length=10), nullable=False, server_default="none"))
    op.alter_column("users", "weigh_reminder", server_default=None)
    op.add_column("users", sa.Column("weigh_weekday", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("weigh_since", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("last_weigh_reminder", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("utc_offset_min", sa.Integer(), nullable=True))


def downgrade() -> None:
    for column in ("utc_offset_min", "last_weigh_reminder", "weigh_since", "weigh_weekday", "weigh_reminder"):
        op.drop_column("users", column)
