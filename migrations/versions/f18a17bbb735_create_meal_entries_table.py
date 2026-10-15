"""create meal_entries table

Revision ID: f18a17bbb735
Revises: a4703dd248ca
Create Date: 2026-10-15 19:52:35.650426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f18a17bbb735'
down_revision: Union[str, None] = 'a4703dd248ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "meal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dish_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("photo_file_id", sa.String(length=200), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("protein_g", sa.Integer(), nullable=False),
        sa.Column("fat_g", sa.Integer(), nullable=False),
        sa.Column("carbs_g", sa.Integer(), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_meal_entries_user_id", "meal_entries", ["user_id"])
    op.create_index("ix_meal_entries_logged_at", "meal_entries", ["logged_at"])


def downgrade() -> None:
    op.drop_index("ix_meal_entries_logged_at", table_name="meal_entries")
    op.drop_index("ix_meal_entries_user_id", table_name="meal_entries")
    op.drop_table("meal_entries")
