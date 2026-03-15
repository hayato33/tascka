"""タスクのビジネスロジック（Business層）。

なぜservices層が必要なのか:
- routes層（API）とcrud層（DB操作）の間にservices層を挟むことで、
  ビジネスロジックの置き場所を明確にする。
- 現時点ではロジックが薄く、crudの委譲がほとんどだが、
  アプリが成長すると「タスク作成時にタグも同時に紐付ける」
  「ステータス変更時に通知を送る」等の複合処理が増える。
  その時にservices層がないと、routes層が肥大化してテストしにくくなる。
- routes層は「HTTPリクエスト/レスポンスの変換」だけに集中し、
  ビジネスロジックはservices層に任せるのが責務分離の原則。

呼び出しルール:
- routes/ → services/ → crud/ の順に呼ぶ
- services/は crud/ を呼ぶが、直接SQLを書かない
- AsyncSessionは引数で受け取る（セッション管理はroutes側のDependsに任せる）
"""

import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tag as tag_crud
from app.crud import task as task_crud
from app.models.tag import Tag
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


async def get_tasks(
    db: AsyncSession,
    *,
    status: TaskStatus | None = None,
    tag: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Task], int]:
    """タスク一覧を取得する。

    この関数がservices層にある理由:
    現時点ではcrudへの委譲だが、将来的にフィルター条件の前処理や
    権限チェック等のロジックが入る可能性がある。
    """
    return await task_crud.get_tasks(
        db, status=status, tag=tag, page=page, per_page=per_page
    )


async def get_task(db: AsyncSession, task_id: uuid.UUID) -> Task:
    """タスクを1件取得する。見つからなければ404を返す。

    この関数がservices層にある理由:
    crud層はNoneを返すだけだが、services層で「見つからない」を
    HTTPExceptionに変換するビジネスルールを担当する。
    """
    task = await task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def _validate_and_get_tags(
    db: AsyncSession, tag_ids: list[uuid.UUID]
) -> list[Tag]:
    """タグIDのリストからタグを取得し、すべてのIDが存在することを検証する。

    存在しないタグIDが含まれている場合は400エラーを返す。
    create_task と update_task の両方で使われる共通バリデーション。
    """
    # 重複を除去して検証（IN句はユニークな結果を返すため、
    # 重複があると件数不一致で誤検知してしまう）
    unique_tag_ids = list(set(tag_ids))
    tags = await tag_crud.get_tags_by_ids(db, unique_tag_ids)
    if len(tags) != len(unique_tag_ids):
        # 存在しなかったIDを特定してエラーメッセージに含める。
        found_ids = {tag.id for tag in tags}
        missing_ids = [str(tid) for tid in unique_tag_ids if tid not in found_ids]
        raise HTTPException(
            status_code=400,
            detail=f"Tags not found: {', '.join(missing_ids)}",
        )
    return tags


async def create_task(db: AsyncSession, task_in: TaskCreate) -> Task:
    """タスクを作成し、タグを紐付ける。

    この関数がservices層にある理由:
    「タスク作成」と「タグ紐付け」という2つのcrud操作を組み合わせる
    複合処理であり、ビジネスロジックに該当する。
    routes層にこのロジックを書くと、routesがDBの詳細を知りすぎてしまう。
    """
    # TaskCreateスキーマからSQLAlchemyモデルを生成する。
    # tag_ids は別途処理するため、excludeで除外する。
    task = Task(**task_in.model_dump(exclude={"tag_ids"}))

    # タグIDが指定されている場合、タグを取得して紐付ける。
    # 存在しないIDが含まれていれば400エラーになる。
    if task_in.tag_ids:
        task.tags = await _validate_and_get_tags(db, task_in.tag_ids)

    return await task_crud.create_task(db, task)


async def update_task(
    db: AsyncSession, task_id: uuid.UUID, task_in: TaskUpdate
) -> Task:
    """タスクを更新する。

    この関数がservices層にある理由:
    「タスク取得」「存在チェック」「タグ再紐付け」「更新」を
    組み合わせた複合処理であり、ビジネスロジックに該当する。
    """
    task = await get_task(db, task_id)

    # exclude_unset=True で、クライアントが送っていないフィールドを除外する。
    # これにより、PATCHリクエストで「送られたフィールドだけ更新」が実現できる。
    update_data = task_in.model_dump(exclude_unset=True, exclude={"tag_ids"})

    # title と status は NOT NULL カラムのため、null での更新を禁止する。
    # PATCH {"title": null} が通ると IntegrityError で500になってしまうため、
    # services層で422に落とす。
    for field in ("title", "status"):
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    # タグIDが明示的に送られた場合のみタグを更新する。
    # 存在しないIDが含まれていれば400エラーになる。
    if task_in.tag_ids is not None:
        task.tags = await _validate_and_get_tags(db, task_in.tag_ids)

    return await task_crud.update_task(db, task, update_data)


async def delete_task(db: AsyncSession, task_id: uuid.UUID) -> None:
    """タスクを削除する。

    この関数がservices層にある理由:
    削除前の存在チェックというビジネスルールを担当する。
    将来的に「完了済みタスクは削除不可」等のルールが追加される可能性がある。
    """
    task = await get_task(db, task_id)
    await task_crud.delete_task(db, task)
