"""タグのCRUD操作（Data層）。

タグに関するDB操作のみを担当する。
ビジネスロジックは services/tag.py に書く。
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag


async def get_tags(db: AsyncSession) -> list[Tag]:
    """タグを全件取得する。

    タグは件数が少ないことを想定しているため、ページネーションは不要。
    """
    query = select(Tag).order_by(Tag.name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_tag(db: AsyncSession, tag_id: uuid.UUID) -> Tag | None:
    """タグをIDで1件取得する。"""
    query = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_tags_by_ids(db: AsyncSession, tag_ids: list[uuid.UUID]) -> list[Tag]:
    """複数のタグIDからタグを一括取得する。

    タスク作成・更新時にタグを紐付ける際に使う。
    IN句で一括取得することで、N+1問題を回避する。
    """
    if not tag_ids:
        return []
    query = select(Tag).where(Tag.id.in_(tag_ids))
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_tag(db: AsyncSession, tag: Tag) -> Tag:
    """タグを作成する。"""
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag
