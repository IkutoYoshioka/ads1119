"""create grades table

Revision ID: 984bf681e09f
Revises: 2a88fe9ef77f
Create Date: 2025-12-12 16:00:39.652529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '984bf681e09f'
down_revision: Union[str, Sequence[str], None] = '2a88fe9ef77f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "grades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("rank_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_grades_code", "grades", ["code"], unique=True)
    op.create_index("ix_grades_rank_order", "grades", ["rank_order"], unique=False)

    # 任意: 初期投入（最低限G04/G05/G06/EXECなど）
    # op.bulk_insert(...) でも op.execute(...) でもOK


def downgrade():
    op.drop_index("ix_grades_rank_order", table_name="grades")
    op.drop_index("ix_grades_code", table_name="grades")
    op.drop_table("grades")
