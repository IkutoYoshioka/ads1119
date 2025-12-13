# app/models/grade.py
from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Grade(Base):
    """
    人事等級マスタ
    例: code="G04", name="4等級", rank_order=4
    """
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)

    # 表示・参照用（人事システムの等級コード）
    code = Column(String(20), unique=True, index=True, nullable=False)

    # 任意（日本語ラベル等）
    name = Column(String(100), nullable=False)

    # 比較・ソート用（等級の序列を明示）
    # 例: G04->4, G06->6, 役員->99 など
    rank_order = Column(Integer, index=True, nullable=False)

    # マスタ運用（論理削除）
    is_active = Column(Boolean, nullable=False, default=True)

    # 恒常ロール
    # employee / site_head / exective
    role_key = Column(String(30), nullable=False, default="employee", index=True)

    # 考課者メニューを表示する等級か
    can_evaluate = Column(Boolean, nullable=False, default=False, index=True)

    # 原則として考課に参加するか
    default_participates = Column(Boolean, nullable=False, default=True, index=True)

    # 評価上の等級コード（4s/5sをG04/G05として扱う）
    evaluated_as_grade_code = Column(String(20), nullable=True)

    # --- relationships ---
    employees = relationship("Employee", back_populates="grade")
    
