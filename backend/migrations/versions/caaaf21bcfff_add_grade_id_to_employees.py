"""add grade_id to employees

Revision ID: caaaf21bcfff
Revises: 85912ee55d65
Create Date: 2025-12-12 16:24:58.965351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caaaf21bcfff'
down_revision: Union[str, Sequence[str], None] = '85912ee55d65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1) grade_id を追加（いったんNULL許容）
    op.add_column("employees", sa.Column("grade_id", sa.Integer(), nullable=True))
    op.create_index("ix_employees_grade_id", "employees", ["grade_id"], unique=False)
    op.create_foreign_key(
        "fk_employees_grade_id",
        "employees",
        "grades",
        ["grade_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # 2) 既存の employees.grade（文字列コード）から grade_id を埋める
    # employees.grade が "G06" 等、grades.code に一致する前提
    op.execute("""
        UPDATE employees e
        SET grade_id = g.id
        FROM grades g
        WHERE e.grade = g.code
    """)

    # 3) grade_id が埋まっていない行があると NOT NULL 化で落ちるため、念のためチェック
    # （開発DBなのでここで落ちてもOKだが、原因が分かるようにする）
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM employees WHERE grade_id IS NULL) THEN
                RAISE EXCEPTION 'employees.grade_id is NULL for some rows. Check employees.grade / grades.code mapping.';
            END IF;
        END
        $$;
    """)

    # 4) NOT NULL 化
    op.alter_column("employees", "grade_id", nullable=False)

    # 5) 旧 grade 列を削除（もう使わない）
    op.drop_column("employees", "grade")


def downgrade():
    # downgrade は簡略（必要なら復元ロジックを書く）
    op.add_column("employees", sa.Column("grade", sa.String(length=20), nullable=True))
    op.execute("""
        UPDATE employees e
        SET grade = g.code
        FROM grades g
        WHERE e.grade_id = g.id
    """)
    op.alter_column("employees", "grade", nullable=False)

    op.drop_constraint("fk_employees_grade_id", "employees", type_="foreignkey")
    op.drop_index("ix_employees_grade_id", table_name="employees")
    op.drop_column("employees", "grade_id")
