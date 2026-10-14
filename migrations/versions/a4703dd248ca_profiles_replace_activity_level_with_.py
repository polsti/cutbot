"""profiles: replace activity_level with granular activity factors

Revision ID: a4703dd248ca
Revises: 2fb15011f51b
Create Date: 2026-10-14 17:19:24.490298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4703dd248ca'
down_revision: Union[str, None] = '2fb15011f51b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("profiles", "activity_level")
    op.add_column("profiles", sa.Column("job_type", sa.String(length=10), nullable=False, server_default="office"))
    op.add_column("profiles", sa.Column("strength_freq", sa.String(length=5), nullable=False, server_default="0"))
    op.add_column("profiles", sa.Column("cardio_freq", sa.String(length=5), nullable=False, server_default="0"))
    op.add_column("profiles", sa.Column("steps_bucket", sa.String(length=15), nullable=False, server_default="<5000"))
    op.add_column("profiles", sa.Column("activity_coefficient", sa.Float(), nullable=False, server_default="1.2"))

    # server_default above was only to satisfy NOT NULL on old rows; new rows always set it explicitly.
    op.alter_column("profiles", "job_type", server_default=None)
    op.alter_column("profiles", "strength_freq", server_default=None)
    op.alter_column("profiles", "cardio_freq", server_default=None)
    op.alter_column("profiles", "steps_bucket", server_default=None)
    op.alter_column("profiles", "activity_coefficient", server_default=None)


def downgrade() -> None:
    op.drop_column("profiles", "activity_coefficient")
    op.drop_column("profiles", "steps_bucket")
    op.drop_column("profiles", "cardio_freq")
    op.drop_column("profiles", "strength_freq")
    op.drop_column("profiles", "job_type")
    op.add_column("profiles", sa.Column("activity_level", sa.String(length=20), nullable=False, server_default="sedentary"))
    op.alter_column("profiles", "activity_level", server_default=None)
