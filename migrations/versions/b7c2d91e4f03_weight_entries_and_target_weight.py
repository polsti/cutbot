"""weight_entries table + profiles.target_weight_kg

Revision ID: b7c2d91e4f03
Revises: e39dcf06b342
Create Date: 2026-10-19 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c2d91e4f03'
down_revision: Union[str, None] = 'e39dcf06b342'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "weight_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_weight_entries_user_id", "weight_entries", ["user_id"])
    op.create_index("ix_weight_entries_recorded_at", "weight_entries", ["recorded_at"])
    op.add_column("profiles", sa.Column("target_weight_kg", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("profiles", "target_weight_kg")
    op.drop_index("ix_weight_entries_recorded_at", table_name="weight_entries")
    op.drop_index("ix_weight_entries_user_id", table_name="weight_entries")
    op.drop_table("weight_entries")
