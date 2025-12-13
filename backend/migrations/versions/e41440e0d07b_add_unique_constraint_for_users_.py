"""add unique constraint for users.employee_id

Revision ID: e41440e0d07b
Revises: 984bf681e09f
Create Date: 2025-12-12 16:02:40.395875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e41440e0d07b'
down_revision: Union[str, Sequence[str], None] = '984bf681e09f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_unique_constraint("uq_users_employee_id", "users", ["employee_id"])


def downgrade():
    op.drop_constraint("uq_users_employee_id", "users", type_="unique")