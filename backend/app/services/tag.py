"""タグのビジネスロジック（Business層）。

なぜservices層が必要なのか:
- routes層とcrud層の間に置くことで、ビジネスロジックの置き場所を明確にする。
- タグは現時点ではシンプルなCRUDだが、将来的に
  「同名タグの重複チェック」「タグ使用中の削除制限」等のルールが入る可能性がある。
- services層を用意しておくことで、routes層を変更せずにロジックを追加できる。
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tag as tag_crud
from app.models.tag import Tag
from app.schemas.tag import TagCreate


async def get_tags(db: AsyncSession) -> list[Tag]:
    """タグ一覧を取得する。

    この関数がservices層にある理由:
    現時点ではcrudへの委譲だが、将来的にフィルター処理や
    ソートロジックが追加される可能性がある。
    """
    return await tag_crud.get_tags(db)


async def create_tag(db: AsyncSession, tag_in: TagCreate) -> Tag:
    """タグを作成する。

    この関数がservices層にある理由:
    TagCreateスキーマからSQLAlchemyモデルへの変換は
    ビジネスロジックの一部であり、crud層の責務ではない。
    """
    tag = Tag(**tag_in.model_dump())
    return await tag_crud.create_tag(db, tag)
