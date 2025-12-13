"""seed grades

Revision ID: 85912ee55d65
Revises: e41440e0d07b
Create Date: 2025-12-12 16:12:55.085415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85912ee55d65'
down_revision: Union[str, Sequence[str], None] = 'e41440e0d07b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    grades = sa.table(
        "grades",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("rank_order", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        grades,
        [
            {"code": "G04", "name": "4等級", "rank_order": 4, "is_active": True},
            {"code": "G05", "name": "5等級", "rank_order": 5, "is_active": True},
            {"code": "G06", "name": "6等級（施設長）", "rank_order": 6, "is_active": True},
            {"code": "EXEC", "name": "役員", "rank_order": 99, "is_active": True},
        ],
    )


def downgrade():
    op.execute("DELETE FROM grades WHERE code IN ('G04','G05','G06','EXEC')")