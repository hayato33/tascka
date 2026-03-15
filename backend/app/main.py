"""FastAPIアプリケーションのエントリーポイント。

このファイルでは以下を行う:
1. lifespan（ライフスパン）でアプリの起動・終了時の処理を定義
2. FastAPIアプリケーションインスタンスの生成
3. CORSミドルウェアの設定
4. ルーターの登録

lifespanとは:
- FastAPIアプリケーションの「起動時」と「終了時」に実行される処理を定義する仕組み。
- 以前は @app.on_event("startup") / @app.on_event("shutdown") を使っていたが、
  FastAPI 0.93+ では lifespan コンテキストマネージャが推奨されている。
- コンテキストマネージャを使うことで、起動と終了の処理を1つの関数にまとめられ、
  リソースの確保と解放が対になっていることが明確になる。
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import tags, tasks
from app.core.config import settings
from app.db.session import engine

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフスパン管理。

    yield の前: アプリ起動時の処理（リソースの初期化）
    yield の後: アプリ終了時の処理（リソースのクリーンアップ）

    asynccontextmanager デコレータにより、
    この非同期ジェネレータ関数をコンテキストマネージャとして使える。
    """
    # --- 起動時 ---
    logger.info("Application starting up")
    yield
    # --- 終了時 ---
    # エンジンのコネクションプールを明示的に閉じる。
    # これを行わないと、アプリ終了時にコネクションがリークする可能性がある。
    await engine.dispose()
    logger.info("Application shut down")


# FastAPIインスタンスを生成する。
# lifespan 引数に上で定義したライフスパン関数を渡す。
# title と version は Swagger UI のドキュメントに表示される。
app = FastAPI(
    title="Tascka API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORSMiddleware を追加して、フロントエンド（別オリジン）からのリクエストを許可する。
#
# CORSとは:
# ブラウザはセキュリティのため、異なるオリジン（ドメイン:ポート）へのリクエストを
# デフォルトでブロックする。フロントエンド（localhost:3000）から
# バックエンド（localhost:8000）へのリクエストは「クロスオリジン」になるため、
# バックエンド側でCORSを明示的に許可する必要がある。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include_router() でルーターを登録する。
# 各ルーターに設定した prefix がそのまま使われる。
# これにより、main.py はルーティングの詳細を知る必要がない。
app.include_router(tasks.router)
app.include_router(tags.router)
