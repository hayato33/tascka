"""タグ用Pydanticスキーマ定義。

タグのAPI入出力データの型を定義する。
タスクスキーマ（schemas/task.py）から参照されるため、
循環インポートを避けるためにタグスキーマを先に定義する。
"""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    """タグ作成リクエストのスキーマ。"""

    name: str = Field(..., min_length=1, max_length=50)


class TagResponse(BaseModel):
    """タグレスポンスのスキーマ。

    from_attributes=True で SQLAlchemy モデルから直接変換可能にする。
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
