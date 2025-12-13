from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Employee(Base):
    """
    従業員プロファイル（人事情報）用モデル。

    - 認証や権限、IP制限などは User に委譲
    - Employee は「誰が」「どの事業所で」「どのグレードで働いているか」を表す
    """

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    # 社員コード（人事側で使うID）
    employee_code = Column(String(50), unique=True, index=True, nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # 等級
    grade_id = Column(Integer, ForeignKey("grades.id", ondelete="RESTRICT"), nullable=False, index=True)

    # アルバイト・パートは基本人事考課に参加しないが、人によっては参加する
    participates_in_evaluation = Column(Boolean, nullable=True, default=None)


    # 所属事業所
    office_id = Column(Integer, ForeignKey("offices.id"), nullable=False)

    # 任意：在籍状況など（将来拡張用）
    status = Column(String(20), nullable=False, default="active")  # active, retired, leave 等
    hired_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # リレーション
    office = relationship("Office", back_populates="employees")
    grade = relationship("Grade", back_populates="employees")

    # 認証アカウント（User）との 1:1 関係
    user = relationship(
        "User",
        back_populates="employee",
        uselist=False,
    )

    # 将来：人事考課関連（割り当て・結果など）もここにぶら下げる想定
    # assignments = relationship("Assignment", back_populates="employee")
    # evaluation_results = relationship("EvaluationResult", back_populates="employee")
