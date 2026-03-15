"""Tagモデルと中間テーブル（task_tags）の定義。

タスクとタグは多対多（Many-to-Many）の関係にある。
例: 1つのタスクに複数のタグを付けられ、1つのタグは複数のタスクに紐付く。

多対多の関係をRDBで表現するには「中間テーブル」が必要。
中間テーブルは2つのテーブルの主キーを外部キーとして持ち、
関連を管理する。ビジネスロジック上の属性は持たない。
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.task import Task

# 中間テーブルの定義。
# 独自のモデルクラスを作らず、Table() で直接テーブルを定義する。
# これはSQLAlchemyの推奨パターンで、中間テーブルに独自の属性（例: 作成日時）が
# 不要な場合に使う。独自属性が必要な場合はモデルクラスとして定義する。
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column(
        "task_id",
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tag(Base):
    """タグテーブルのモデル。

    タグ名はユニーク制約を設定し、同じ名前のタグが重複しないようにする。
    """

    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # unique=True でユニーク制約を設定。
    # 同じ名前のタグをINSERTしようとするとDBレベルでエラーになる。
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Task側の relationship と対になる定義。
    # back_populates="tags" で Task.tags と双方向に紐付く。
    tasks: Mapped[list["Task"]] = relationship(
        secondary="task_tags",
        back_populates="tags",
        lazy="selectin",
    )
