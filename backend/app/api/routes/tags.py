"""タグエンドポイント（Presentation層）。

タグの一覧取得と作成のエンドポイントを定義する。
タスクと同様に、ビジネスロジックは services/ に委譲する。
"""

from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.tag import TagCreate, TagResponse
from app.services import tag as tag_service

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(
    db: DbSession,
) -> list[TagResponse]:
    """タグ一覧を取得する。

    タグは件数が少ない想定のため、ページネーションなしで全件返す。
    response_model=list[TagResponse] で、レスポンスの型を明示する。
    FastAPIはこの型に基づいてSwagger UIのドキュメントを自動生成する。
    """
    tags = await tag_service.get_tags(db)
    return [TagResponse.model_validate(t) for t in tags]


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    db: DbSession,
    tag_in: TagCreate,
) -> TagResponse:
    """タグを作成する。

    タグ名が重複した場合は、DBのUNIQUE制約によりエラーになる。
    SQLAlchemyがIntegrityErrorを発生させるので、
    必要に応じてservices層でキャッチしてHTTPExceptionに変換する。
    """
    tag = await tag_service.create_tag(db, tag_in)
    return TagResponse.model_validate(tag)
