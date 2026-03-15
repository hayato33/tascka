# Tascka（タスカ）

Next.js + FastAPI + PostgreSQL によるタスク管理アプリ。

フレームワークのお作法・基本実装パターンの習得を目的としたプロジェクトです。

## 技術スタック

| 領域 | 技術 |
|------|------|
| Frontend | Next.js 14 (App Router), TypeScript, TanStack Query v5, Zustand, React Hook Form + Zod, Tailwind CSS, shadcn/ui |
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.x (async), Alembic, Pydantic v2, structlog |
| Database | PostgreSQL 16 |
| Infrastructure | Podman + podman-compose, Makefile, direnv |

## 前提条件

以下がインストールされていること:

- **Node.js** 20+
- **Python** 3.12+
- **uv** (Python パッケージマネージャ)
- **Podman** + **podman-compose**
- **direnv**

## セットアップ

```bash
# 1. リポジトリをクローン
git clone git@github.com:hayato33/tascka.git
cd tascka

# 2. 環境変数の設定
cp .envrc.example .envrc
direnv allow

# 3. DBコンテナ起動
make up

# 4. バックエンドのセットアップ
cd backend
uv sync
cd ..

# 5. フロントエンドのセットアップ
cd frontend
npm install
cd ..

# 6. DBマイグレーション
make migrate
```

## 開発コマンド

```bash
make up          # PostgreSQLコンテナ起動
make down        # PostgreSQLコンテナ停止
make be          # バックエンド開発サーバー起動 (localhost:8000)
make fe          # フロントエンド開発サーバー起動 (localhost:3000)
make migrate     # Alembicマイグレーション実行
make gen-api     # OpenAPI型自動生成
make lint        # Ruff + ESLint
make test        # pytest
```

## 開発サーバー

| サービス | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend (Swagger UI) | http://localhost:8000/docs |

## アーキテクチャ

### Backend 3層構成

```text
routes/   → リクエスト受付・レスポンス返却        (Presentation層)
services/ → ビジネスロジック・複数crud操作の組合せ  (Business層)
crud/     → DB操作ロジック                       (Data層)
```

呼び出しは `routes → services → crud` の順。routes から crud を直接呼ばない。

### Frontend features構成

```text
features/{機能名}/
  ├── api/          # TanStack Query Hooks
  ├── components/   # UIコンポーネント
  ├── stores/       # Zustand store
  └── types/        # 型定義
```

サーバーデータは TanStack Query、UI状態は Zustand で管理（責務分離）。

## API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| GET | `/api/tasks` | タスク一覧（ページネーション・フィルター対応） |
| POST | `/api/tasks` | タスク作成 |
| GET | `/api/tasks/{id}` | タスク詳細 |
| PATCH | `/api/tasks/{id}` | タスク部分更新 |
| DELETE | `/api/tasks/{id}` | タスク削除 |
| GET | `/api/tags` | タグ一覧 |
| POST | `/api/tags` | タグ作成 |

## Git 規約

[Conventional Commits](https://www.conventionalcommits.org/) に準拠。commitlint で強制。

```
feat: 新機能
fix: バグ修正
docs: ドキュメント
chore: その他
refactor: リファクタリング
test: テスト
```
