"""データベースセッション管理モジュール。

SQLAlchemy 2.x の非同期セッションを設定し、
FastAPIのDI（Depends）で注入するためのジェネレータ関数を提供する。

なぜ非同期（async）でDB接続するのか:
- FastAPIは非同期フレームワークであり、I/O待ち（DB問い合わせ等）の間に
  他のリクエストを処理できる。同期的にDB接続するとその間スレッドがブロックされ、
  FastAPIの非同期の恩恵を受けられない。
- asyncpg は PostgreSQL 用の高速な非同期ドライバ。
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# create_async_engine() で非同期用のエンジンを生成する。
# エンジンはDB接続プールを管理し、アプリ全体で1つだけ生成する。
#
# echo: SQLAlchemyが発行するSQLをログに出力するかどうか。環境変数で切り替え可能。
# pool_pre_ping: 接続を使う前にDBへの疎通確認（SELECT 1）を行う。
#   DBが再起動された等で接続が切れていた場合、自動的に再接続してくれる。
#   本番環境で接続エラーを防ぐために重要。
# pool_size: コネクションプールに保持する接続数。デフォルトは5。
# max_overflow: pool_size を超えた場合に一時的に追加できる接続数。
engine = create_async_engine(
    settings.database_url,
    echo=settings.sql_echo,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# async_sessionmaker は、AsyncSession のファクトリ（生成器）。
# expire_on_commit=False にすると、commit後もオブジェクトの属性にアクセスできる。
# デフォルト（True）だと、commit後にアクセスすると遅延ロードが走るが、
# 非同期セッションでは遅延ロードがサポートされないためエラーになる。
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPIのDepends()で使うDBセッションジェネレータ。

    Depends() はFastAPIのDI（依存性注入）の仕組み。
    エンドポイントの引数に Depends(get_db) と書くだけで、
    FastAPIがリクエストごとに自動でDBセッションを生成・注入・クローズしてくれる。
    手動で session.close() を書く必要がなく、例外時も確実にクリーンアップされる。

    yieldを使ったジェネレータにすることで:
    1. yield前: セッションを生成してエンドポイントに渡す
    2. yield中: エンドポイントの処理が実行される
    3. yield後（async withの__aexit__）: セッションが自動的にクローズされる
    """
    async with AsyncSessionLocal() as session:
        yield session
