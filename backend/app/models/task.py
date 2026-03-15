"""Taskモデル定義。

SQLAlchemy 2.x の Mapped 型アノテーションを使ったモデル定義。
SQLAlchemy 2.x では、従来の Column() ベースの定義に加えて、
Pythonの型ヒントを活用した Mapped[] による定義が推奨されている。

なぜ Mapped[] を使うのか:
- 型チェッカー（pyright等）がカラムの型を認識できるようになる
- Column() だけだと型チェッカーは型を推論できない
- mapped_column() は Column() の後継で、型ヒントと連携する
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.tag import Tag


class TaskStatus(str, enum.Enum):
    """タスクのステータスを表すEnum。

    str を継承しているのは、JSON シリアライズ時に自動で文字列に変換されるようにするため。
    Pydanticがこの値を扱うときにも、文字列として自然にシリアライズされる。
    """

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    """タスクテーブルのモデル。

    __tablename__ でテーブル名を指定する。
    SQLAlchemyはこの値を使ってCREATE TABLE文を生成する。
    """

    __tablename__ = "tasks"

    # UUIDを主キーとして使用。
    # default=uuid.uuid4 により、Python側でINSERT時に自動生成される。
    # データベース側のdefaultではなくPython側で生成するため、
    # INSERT前にIDを参照できるメリットがある。
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional な型には `| None` を使い、nullable=True を明示する。
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # SQLAlchemy の Enum 型を使うと、DBレベルでENUM型のカラムが作られる。
    # Mapped[TaskStatus] と書くことで、SQLAlchemyが自動的にEnum型を推論する。
    status: Mapped[TaskStatus] = mapped_column(
        default=TaskStatus.TODO,
    )

    # server_default=func.now() はDBサーバー側でデフォルト値を生成する。
    # Pythonの datetime.now() と違い、DBサーバーの時刻を使うため、
    # アプリサーバーとDBサーバーの時刻ずれの影響を受けない。
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    # onupdate=func.now() は、SQLAlchemyがUPDATE文を発行する際に
    # 自動的に現在時刻をセットしてくれる機能。
    # server_default も設定しているのは、INSERT時にもnullにならないようにするため。
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    # relationship() はSQLAlchemy ORMのリレーション定義。
    # secondary にはMany-to-Manyの中間テーブルを指定する。
    # back_populates で双方向のリレーションを張る（Tag.tasks と対応）。
    #
    # lazy="selectin" は、タスクを取得する際にタグも一緒に
    # SELECT ... FROM tags WHERE tag_id IN (...) で効率的に取得する戦略。
    # 非同期セッションでは遅延ロード（lazy="select"）が使えないため、
    # "selectin" や "joined" などの即時ロード戦略を指定する必要がある。
    tags: Mapped[list["Tag"]] = relationship(
        secondary="task_tags",
        back_populates="tasks",
        lazy="selectin",
    )
