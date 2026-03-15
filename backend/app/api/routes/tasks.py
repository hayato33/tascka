"""タスクエンドポイント（Presentation層）。

FastAPIのAPIRouter を使ってエンドポイントを定義するモジュール。
このモジュールの責務は:
- HTTPリクエストの受付とパラメータの取得
- services層の呼び出し
- HTTPレスポンスの返却

ビジネスロジックやDB操作はここには書かない。
すべて services/ 経由で処理する。

APIRouter を使う理由:
- エンドポイントをファイルごとに分割できる
- main.py で include_router() するだけで登録できる
- prefix や tags を設定してSwagger UIでグループ化できる
"""

import uuid

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services import task as task_service

# prefix="/api/tasks" で、このルーターのすべてのエンドポイントに
# /api/tasks というプレフィックスが自動的に付く。
# tags=["tasks"] は Swagger UI でエンドポイントをグループ化するためのラベル。
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    db: DbSession,
    status: TaskStatus | None = None,
    tag: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> TaskListResponse:
    """タスク一覧を取得する。

    FastAPIはクエリパラメータを関数の引数として自動的にパースする。
    Query() を使うことで、バリデーション（ge=1: 1以上）やデフォルト値を指定できる。
    型ヒント（TaskStatus | None）により、不正な値が送られた場合は
    FastAPIが自動的に422 Validation Errorを返す。
    """
    tasks, total = await task_service.get_tasks(
        db, status=status, tag=tag, page=page, per_page=per_page
    )
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    db: DbSession,
    task_in: TaskCreate,
) -> TaskResponse:
    """タスクを作成する。

    リクエストボディは task_in: TaskCreate として受け取る。
    FastAPIはリクエストのJSON bodyを自動的にPydanticモデルに変換する。
    バリデーションエラーの場合は自動的に422を返す。

    status_code=201 で、成功時に201 Createdを返すことを明示する。
    デフォルトは200だが、リソース作成時は201が適切。
    """
    task = await task_service.create_task(db, task_in)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    db: DbSession,
    task_id: uuid.UUID,
) -> TaskResponse:
    """タスクを1件取得する。

    パスパラメータ {task_id} は関数の引数名と一致させる。
    FastAPIが自動的にUUIDに変換し、不正な形式なら422を返す。
    タスクが見つからない場合は、services層でHTTPException(404)が発生する。
    """
    task = await task_service.get_task(db, task_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    db: DbSession,
    task_id: uuid.UUID,
    task_in: TaskUpdate,
) -> TaskResponse:
    """タスクを部分更新する。

    PATCHメソッドは「部分更新」を意味する（PUTは「全体置換」）。
    TaskUpdateスキーマはすべてのフィールドがOptionalなので、
    クライアントは変更したいフィールドだけ送ればよい。
    """
    task = await task_service.update_task(db, task_id, task_in)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    db: DbSession,
    task_id: uuid.UUID,
) -> None:
    """タスクを削除する。

    status_code=204 (No Content) は、成功したがレスポンスボディがないことを示す。
    削除成功時はボディを返す必要がないため、204が適切。
    戻り値の型を None にすることで、FastAPIはレスポンスボディを返さない。
    """
    await task_service.delete_task(db, task_id)
