"""Alembicの環境設定ファイル。

このファイルはAlembicがマイグレーションを実行する際に読み込まれる。
SQLAlchemyのモデル定義（metadata）を参照して、
現在のDBスキーマとの差分を検出し、マイグレーションスクリプトを生成する。

非同期（asyncpg）に対応するため、run_async_migrations() で
非同期エンジンを使ってマイグレーションを実行する。
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings

# Alembicの設定オブジェクトを取得
config = context.config

# ロギング設定を読み込む
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# alembic.ini の sqlalchemy.url を動的に上書きする。
# これにより、環境変数で接続先を切り替えられる。
config.set_main_option("sqlalchemy.url", settings.database_url)

# SQLAlchemyのモデル定義を読み込む。
# models/__init__.py ですべてのモデルをインポートしているため、
# Base.metadata にすべてのテーブル定義が含まれる。
from app.models.base import Base  # noqa: E402

# Alembicがマイグレーションの自動生成時に参照するメタデータ。
# これがないと、Alembicはモデルの変更を検出できない。
import app.models  # noqa: E402, F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """オフラインモードでマイグレーションを実行する。

    DBに接続せず、SQL文だけを生成するモード。
    CI/CDでSQL文のレビューが必要な場合等に使う。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """マイグレーションの実行（同期部分）。

    connectable.connect() で取得したコネクションを使って
    マイグレーションを実行する。
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """非同期エンジンでマイグレーションを実行する。

    asyncpg は非同期ドライバなので、通常の同期的なマイグレーション実行が使えない。
    async_engine_from_config() で非同期エンジンを作り、
    conn.run_sync() で同期的なマイグレーション関数を実行する。
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """オンラインモードでマイグレーションを実行する。

    通常のマイグレーション実行はこちらが使われる。
    asyncio.run() で非同期のマイグレーション関数を実行する。
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
