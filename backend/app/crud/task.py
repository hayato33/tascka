"""タスクのCRUD操作（Data層）。

このモジュールはDB操作のみを担当する。
ビジネスロジック（例: 「ステータスがdoneのタスクは編集不可」等のルール）は
ここには書かず、services層に書く。

なぜcrud層を分けるのか:
- DB操作とビジネスロジックを混ぜると、テストが難しくなる
- DB操作を関数として切り出すことで、異なるservicesから再利用できる
- 責務が明確になり、「このバグはDB操作の問題か、ロジックの問題か」を切り分けやすい
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tag import Tag
from app.models.task import Task, TaskStatus


async def get_tasks(
    db: AsyncSession,
    *,
    status: TaskStatus | None = None,
    tag: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Task], int]:
    """タスクを一覧取得する（フィルター・ページネーション対応）。

    AsyncSessionを引数で受け取るのは、セッションのライフサイクル管理を
    呼び出し元（routes層のDepends）に任せるため。
    crud層がセッションを生成・管理すると、トランザクション境界の制御が難しくなる。

    Returns:
        タスクのリストと総件数のタプル
    """
    # select() でSQLのSELECT文を構築する。
    # SQLAlchemy 2.x では、query() の代わりに select() を使うのが推奨。
    query = select(Task)

    # フィルター条件を動的に追加する。
    # where() を連鎖させることで、条件がANDで結合される。
    if status is not None:
        query = query.where(Task.status == status)

    if tag is not None:
        # タグ名でフィルターする場合、Task.tags リレーションを使って
        # JOINし、Tag.name で絞り込む。
        query = query.where(Task.tags.any(Tag.name == tag))

    # 総件数を取得するクエリ。
    # select(func.count()) でCOUNT(*)相当のクエリを作る。
    # .select_from(query.subquery()) で元のクエリの結果をサブクエリとして使う。
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # ページネーション: offset と limit でページ分割する。
    # offset = (page - 1) * per_page で、指定ページの先頭位置を計算する。
    query = (
        query.options(selectinload(Task.tags))
        .order_by(Task.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    # await db.execute() で実際にSQLを発行する。
    # awaitが必要なのは、asyncpg が非同期I/OでDBと通信するため。
    result = await db.execute(query)

    # scalars() は結果を ORM モデルオブジェクトとして取得するメソッド。
    # execute() の結果は Row オブジェクトだが、scalars() で最初のカラム（Taskオブジェクト）
    # だけを取り出す。all() でリストに変換する。
    tasks = list(result.scalars().all())

    return tasks, total


async def get_task(db: AsyncSession, task_id: uuid.UUID) -> Task | None:
    """タスクをIDで1件取得する。

    見つからない場合は None を返す。
    404のHTTPExceptionを投げるのはservices層またはroutes層の責務。
    crud層はDB操作の結果をそのまま返すだけにする。
    """
    query = select(Task).where(Task.id == task_id).options(selectinload(Task.tags))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_task(db: AsyncSession, task: Task) -> Task:
    """タスクを作成する。

    db.add() でセッションにオブジェクトを追加し、
    db.commit() でトランザクションをコミットする。
    db.refresh() でDB側で生成された値（id, created_at等）を
    オブジェクトに反映する。
    """
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession,
    task: Task,
    update_data: dict,
) -> Task:
    """タスクを更新する。

    setattr() でモデルオブジェクトの属性を動的に更新する。
    SQLAlchemyはcommit時に変更を検知して自動的にUPDATE文を発行する。
    """
    for key, value in update_data.items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    """タスクを削除する。

    db.delete() でセッションから削除をマークし、
    commit() で実際にDELETE文が発行される。
    中間テーブル（task_tags）のレコードは、
    外部キーに ON DELETE CASCADE を設定しているため、
    DBが自動的に削除する。
    """
    await db.delete(task)
    await db.commit()
