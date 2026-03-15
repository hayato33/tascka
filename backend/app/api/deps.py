"""API共通の依存関係（Dependencies）定義。

FastAPIのDI（依存性注入: Dependency Injection）の仕組みを使って、
エンドポイント間で共通の依存関係を定義するモジュール。

Depends() はFastAPIのDIの仕組み。
エンドポイントの引数に Depends(get_db) と書くだけで、
FastAPIがリクエストごとに自動でDBセッションを生成・注入・クローズしてくれる。
手動で session.close() を書く必要がなく、例外時も確実にクリーンアップされる。

なぜDI（依存性注入）を使うのか:
- エンドポイントがDBセッションの「作り方」を知る必要がなくなる
- テスト時にモックのセッションに差し替えるのが容易になる
- セッション管理の重複コードがなくなる
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

# Annotated を使って型と依存関係をまとめて定義する。
# これにより、エンドポイントの引数を `db: DbSession` と書くだけで
# Depends(get_db) が自動適用される。
# Python 3.9+ の typing.Annotated と FastAPI の Depends を組み合わせた
# FastAPI推奨のパターン。
DbSession = Annotated[AsyncSession, Depends(get_db)]
