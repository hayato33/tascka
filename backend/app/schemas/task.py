"""タスク用Pydanticスキーマ定義。

Pydanticスキーマは、APIの入出力データの「型」を定義するもの。
SQLAlchemyのモデル（models/）がDB上のテーブル構造を表すのに対し、
Pydanticスキーマ（schemas/）はAPI通信で使うデータの形を表す。

なぜCreate・Update・Responseを分けるのか:
- Create: ユーザーが作成時に送るデータ（idや日時は含まない）
- Update: ユーザーが更新時に送るデータ（すべてOptionalにしてPATCHに対応）
- Response: APIがクライアントに返すデータ（idや日時を含む）
- 同じスキーマを使い回すと、「作成時にidを送れてしまう」等のバグが起きやすい
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus
from app.schemas.tag import TagResponse


class TaskCreate(BaseModel):
    """タスク作成リクエストのスキーマ。

    クライアントが POST /api/tasks で送るデータの形。
    id, created_at, updated_at はサーバー側で自動生成するため含めない。
    """

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    # タスク作成時にタグIDのリストを渡せるようにする
    tag_ids: list[uuid.UUID] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    """タスク更新リクエストのスキーマ。

    PATCH /api/tasks/{task_id} で送るデータの形。
    PATCHは「部分更新」なので、すべてのフィールドをOptionalにする。
    クライアントは変更したいフィールドだけを送ればよい。
    """

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    tag_ids: list[uuid.UUID] | None = None


class TaskResponse(BaseModel):
    """タスクレスポンスのスキーマ。

    APIがクライアントに返すデータの形。
    id, created_at, updated_at などサーバー側で管理する情報も含む。

    model_config の from_attributes = True は、
    SQLAlchemyのモデルオブジェクトから直接Pydanticモデルに変換するために必要。
    これがないと、task.title のような属性アクセスではなく、
    task["title"] のような辞書アクセスしかできない。
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    # タスクに紐付くタグの一覧も含める
    tags: list[TagResponse] = Field(default_factory=list)


class TaskListResponse(BaseModel):
    """タスク一覧レスポンスのスキーマ。

    ページネーション情報を含むレスポンス。
    """

    items: list[TaskResponse]
    total: int
    page: int
    per_page: int
