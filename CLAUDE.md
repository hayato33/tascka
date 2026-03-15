# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tascka（タスカ）** — Next.js (FE) + FastAPI (BE) + PostgreSQL によるタスク管理アプリ。
目的はフレームワークのお作法・基本実装パターンの習得。コードの可読性・構成の明確さを最優先とする。

## Tech Stack

- **BE**: Python 3.12+, FastAPI, SQLAlchemy 2.x (async), Alembic, Pydantic v2, asyncpg, structlog
- **FE**: Next.js 14 (App Router), TypeScript (strict), TanStack Query v5, Zustand, React Hook Form + Zod, Tailwind CSS, shadcn/ui, nuqs, date-fns
- **Infra**: PostgreSQL 16, Podman + podman-compose, Makefile, direnv

## Common Commands

```bash
make up            # podman-compose up -d (DB起動)
make down          # podman-compose down
make be            # uvicorn起動 (--reload付き)
make fe            # next dev起動
make migrate       # alembic upgrade head
make gen-api       # openapi-typescriptによる型生成
make lint          # ruff + next lint
make test          # pytest

# Backend個別
cd backend && uv run ruff check .          # lint
cd backend && uv run ruff format .         # format
cd backend && uv run pyright               # 型チェック
cd backend && uv run pytest tests/ -x      # テスト実行（最初の失敗で停止）
cd backend && uv run pytest tests/test_foo.py::test_bar -v  # 単一テスト

# Frontend個別
cd frontend && npm run lint                # ESLint
cd frontend && npm run gen:api             # OpenAPI型生成
```

## Architecture

### Backend 3層構成

```
routes/   → リクエスト受付・レスポンス返却        (Presentation層)
schemas/  → 入出力の型定義 (Pydantic)             (Presentation層)
services/ → ビジネスロジック・複数crud操作の組合せ  (Business層)
crud/     → DB操作ロジック (SQLAlchemy)            (Data層)
models/   → テーブル定義 (SQLAlchemyモデル)        (Data層)
```

**呼び出しルール:**
- `routes/` → `services/` → `crud/` の順。routes から crud を直接呼んではいけない
- `services/` と `crud/` は `AsyncSession` を引数で受け取る（セッション管理は routes 側の Depends に任せる）
- schemas は Create用・Update用・Response用を必ず分けて定義する

### Frontend features/ 構成

```
features/{feature}/api/        → TanStack Query Hooks
features/{feature}/components/ → UIコンポーネント
features/{feature}/stores/     → Zustand store
features/{feature}/types/      → openapi-typescriptで生成した型のre-export
```

- サーバーデータは TanStack Query で管理。Zustand にサーバーデータを入れない
- フィルター条件（ステータス・タグ）は nuqs でURLクエリと同期
- fetch の 4xx/5xx ハンドリングは `frontend/lib/api.ts` の共通関数で行う

## Coding Conventions

### Backend コメントポリシー
学習用プロジェクトのため、バックエンドのコメントは通常より大幅に詳細に記載する。以下の観点を必ず含める:
- FastAPI固有の仕組み（Depends, lifespan 等）
- SQLAlchemy固有の挙動（AsyncSession のスコープ, selectinload 等）
- Pydantic の役割（Request/Response スキーマを分ける理由等）
- Python の非同期処理（async def vs def, await が必要な理由）
- 設計上の意図（crud層を分ける理由, DI を使う理由）

### 共通
- 各ファイルの先頭にそのファイルの役割をコメントで明記する
- 型を `any` で誤魔化さない
- 判断が必要な箇所は最もシンプルな実装を選ぶ
- 環境変数で設定を外出しする（DB URL・CORS オリジン等をハードコードしない）
- FE の API エンドポイントは `NEXT_PUBLIC_API_URL` 環境変数で切り替え可能にする

## Git Hooks / Quality

- **FE**: Husky + lint-staged（ESLint・TypeScript型チェック・Prettier）
- **BE**: pre-commit（Ruff・pyright・Alembicチェック）
- **共通**: commitlint で Conventional Commits（`feat:`, `fix:`, `chore:` 等）を強制

## Dev URLs

- Backend Swagger UI: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`
