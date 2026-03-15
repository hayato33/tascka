# Tascka 実装計画書

## プロジェクト概要

**アプリ名**: Tascka（タスカ）
**目的**: Next.js（FE）+ FastAPI（BE）+ PostgreSQL によるタスク管理アプリの構築を通じた、フレームワークのお作法・基本実装パターンの習得
**方針**: コードの可読性・構成の明確さを最優先とする

---

## 技術スタック

### Backend

| カテゴリ | 技術 |
|---------|------|
| Runtime | Python 3.12+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x（非同期） |
| Migration | Alembic |
| Validation | Pydantic v2 |
| DB Driver | asyncpg |
| Settings | pydantic-settings |
| Linter/Formatter | Ruff |
| Type checker | pyright |
| Test | pytest + httpx + pytest-asyncio + factory-boy |
| ログ | structlog |

### Frontend

| カテゴリ | 技術 |
|---------|------|
| Framework | Next.js 14（App Router） |
| Language | TypeScript（strict モード） |
| Server state | TanStack Query v5 |
| Global state | Zustand |
| Form | React Hook Form + Zod |
| Styling | Tailwind CSS |
| UI | shadcn/ui |
| HTTP client | fetch（ネイティブ） |
| API型生成 | openapi-typescript |
| URLクエリ管理 | nuqs |
| 日付 | date-fns |

### Infrastructure

| カテゴリ | 技術 |
|---------|------|
| DB | PostgreSQL 16 |
| Container | Podman + podman-compose |
| Task runner | Makefile |
| Env管理 | direnv（.envrc） |

### Quality / Git hooks

| 対象 | ツール |
|------|--------|
| FE | Husky + lint-staged（ESLint・TypeScript型チェック・Prettier） |
| BE | pre-commit.com（Ruff・pyright・Alembicチェック） |
| 共通 | commitlint（Conventional Commits規約を強制） |

---

## 機能要件

1. タスクの一覧表示（ページネーション・ステータスフィルター）
2. タスクの作成
3. タスクの編集
4. タスクの削除
5. ステータス管理（`todo` / `in_progress` / `done`）
6. タグ付け（タスクとタグは多対多）

---

## ディレクトリ構成

```
/
├── Makefile
├── .envrc
├── podman-compose.yml
├── backend/
│   ├── .env
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   └── app/
│       ├── main.py               # lifespanの定義・ルーター登録・CORS設定
│       ├── core/
│       │   └── config.py         # pydantic-settingsによる設定
│       ├── db/
│       │   └── session.py        # AsyncSession・エンジン・get_db
│       ├── models/
│       │   ├── base.py           # DeclarativeBase
│       │   ├── task.py           # Taskモデル
│       │   └── tag.py            # Tagモデル・中間テーブル
│       ├── schemas/
│       │   ├── task.py           # TaskCreate / TaskUpdate / TaskResponse
│       │   └── tag.py            # TagCreate / TagResponse
│       ├── services/
│       │   ├── task.py           # タスクのビジネスロジック
│       │   └── tag.py            # タグのビジネスロジック
│       ├── crud/
│       │   ├── task.py           # DB操作ロジック
│       │   └── tag.py
│       └── api/
│           ├── deps.py           # Depends用の共通依存（get_db等）
│           └── routes/
│               ├── tasks.py      # タスクエンドポイント
│               └── tags.py       # タグエンドポイント
└── frontend/
    ├── .env.local
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── lib/
    │   └── api.ts                # fetch共通関数
    ├── app/
    │   ├── layout.tsx
    │   ├── providers.tsx          # TanStack Query Provider
    │   ├── page.tsx               # タスク一覧
    │   ├── loading.tsx
    │   ├── error.tsx
    │   └── tasks/
    │       └── [id]/
    │           └── page.tsx       # タスク詳細・編集
    └── features/
        └── tasks/
            ├── api/
            │   └── useTasks.ts    # TanStack QueryのHooks
            ├── components/
            │   ├── TaskList.tsx
            │   ├── TaskCard.tsx
            │   ├── TaskForm.tsx
            │   └── TaskFilter.tsx
            ├── stores/
            │   └── taskFilterStore.ts
            └── types/
                └── index.ts
```

---

## アーキテクチャ方針

### Backend 3層構成

```
routes/   → リクエスト受付・バリデーション・レスポンス返却  （Presentation層）
schemas/  → 入出力の型定義（Pydantic）                    （Presentation層）
services/ → ビジネスロジック・複数crud操作の組み合わせ      （Business層）
crud/     → DB操作ロジック（SQLAlchemy）                  （Data層）
models/   → テーブル定義（SQLAlchemyモデル）               （Data層）
```

**呼び出しルール:**

- `routes/` は `services/` を呼ぶ。crud を直接呼んではいけない
- `services/` は `crud/` を呼ぶ。DBセッションは引数で受け取る
- `crud/` はDB操作のみ。ビジネスルールを持たない
- 現時点ではビジネスロジックが薄いため services はほぼ crud の委譲になるが、層として存在させることで責務の置き場所を明確にする

### Frontend 設計方針

- データフェッチは TanStack Query（Client Component）で行う
- サーバーデータは TanStack Query で管理し、Zustand に入れない（責務の分離）
- フィルター条件（ステータス・タグ）は nuqs でURLクエリパラメータと同期
- fetch の 4xx/5xx ハンドリングは `lib/api.ts` の共通関数で行う

---

## DBスキーマ

### tasks テーブル

| カラム | 型 | 備考 |
|--------|----|------|
| id | UUID | PK, default: uuid4 |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| status | ENUM | `todo` / `in_progress` / `done`, default: `todo` |
| created_at | TIMESTAMP | default: now() |
| updated_at | TIMESTAMP | onupdate: now() |

### tags テーブル

| カラム | 型 | 備考 |
|--------|----|------|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL |

### task_tags テーブル（中間テーブル）

| カラム | 型 | 備考 |
|--------|----|------|
| task_id | UUID | FK → tasks.id, ON DELETE CASCADE |
| tag_id | UUID | FK → tags.id, ON DELETE CASCADE |

---

## APIエンドポイント仕様

### Tasks

| Method | Path | 説明 | レスポンス |
|--------|------|------|-----------|
| GET | `/api/tasks` | 一覧取得 `?status=todo&tag=xxx&page=1&per_page=20` | TaskListResponse |
| POST | `/api/tasks` | 作成 | 201 TaskResponse |
| GET | `/api/tasks/{task_id}` | 詳細取得 | TaskResponse |
| PATCH | `/api/tasks/{task_id}` | 部分更新 | TaskResponse |
| DELETE | `/api/tasks/{task_id}` | 削除 | 204 No Content |

### Tags

| Method | Path | 説明 | レスポンス |
|--------|------|------|-----------|
| GET | `/api/tags` | 一覧取得 | list[TagResponse] |
| POST | `/api/tags` | 作成 | 201 TagResponse |

---

## 実装順序

### Phase 1: インフラ・環境構築

| # | ファイル | 内容 |
|---|---------|------|
| 1-1 | `podman-compose.yml` | PostgreSQL 16 コンテナ定義 |
| 1-2 | `Makefile` | 共通タスクランナー（up/down/be/fe/migrate/gen-api/lint/test） |
| 1-3 | `.envrc` | direnv用環境変数 |
| 1-4 | `.gitignore` | Git除外設定 |

### Phase 2: Backend基盤

| # | ファイル | 内容 |
|---|---------|------|
| 2-1 | `backend/pyproject.toml` | 依存関係定義 |
| 2-2 | `backend/Dockerfile` | デプロイ用コンテナ定義 |
| 2-3 | `app/core/config.py` | pydantic-settingsによる環境変数読み込み |
| 2-4 | `app/db/session.py` | AsyncSession・エンジン・get_dbジェネレータ |

### Phase 3: Backend モデル・スキーマ

| # | ファイル | 内容 |
|---|---------|------|
| 3-1 | `app/models/base.py` | DeclarativeBase定義 |
| 3-2 | `app/models/task.py` | Taskモデル（TaskStatus Enum含む） |
| 3-3 | `app/models/tag.py` | Tagモデル・task_tags中間テーブル |
| 3-4 | `app/schemas/tag.py` | TagCreate / TagResponse |
| 3-5 | `app/schemas/task.py` | TaskCreate / TaskUpdate / TaskResponse / TaskListResponse |

### Phase 4: Backend ビジネスロジック

| # | ファイル | 内容 |
|---|---------|------|
| 4-1 | `app/crud/task.py` | タスクのDB操作（一覧・詳細・作成・更新・削除） |
| 4-2 | `app/crud/tag.py` | タグのDB操作（一覧・作成・ID一括取得） |
| 4-3 | `app/services/task.py` | タスクのビジネスロジック（crud組み合わせ・存在チェック） |
| 4-4 | `app/services/tag.py` | タグのビジネスロジック |

### Phase 5: Backend API

| # | ファイル | 内容 |
|---|---------|------|
| 5-1 | `app/api/deps.py` | Depends用共通依存（DbSession型エイリアス） |
| 5-2 | `app/api/routes/tasks.py` | タスクエンドポイント（5エンドポイント） |
| 5-3 | `app/api/routes/tags.py` | タグエンドポイント（2エンドポイント） |
| 5-4 | `app/main.py` | lifespan・CORS・ルーター登録 |

### Phase 6: Alembic

| # | ファイル | 内容 |
|---|---------|------|
| 6-1 | `alembic.ini` | Alembic設定 |
| 6-2 | `alembic/env.py` | 非同期対応のマイグレーション環境設定 |
| 6-3 | `alembic/script.py.mako` | マイグレーションテンプレート |
| 6-4 | — | 初回マイグレーションファイル自動生成（`alembic revision --autogenerate`） |

### Phase 7: Frontend基盤

| # | ファイル | 内容 |
|---|---------|------|
| 7-1 | `frontend/package.json` | 依存関係・scripts定義 |
| 7-2 | `frontend/tsconfig.json` | TypeScript strict設定 |
| 7-3 | `frontend/tailwind.config.ts` | Tailwind CSS設定 |
| 7-4 | `frontend/next.config.js` | Next.js設定 |
| 7-5 | `frontend/lib/api.ts` | fetch共通関数（4xx/5xxハンドリング） |

### Phase 8: Frontend ページ・Provider

| # | ファイル | 内容 |
|---|---------|------|
| 8-1 | `app/layout.tsx` | ルートレイアウト（メタデータ・Provider） |
| 8-2 | `app/providers.tsx` | QueryClientProvider設定 |
| 8-3 | `app/page.tsx` | タスク一覧ページ |
| 8-4 | `app/loading.tsx` | ローディングUI（Suspense連携） |
| 8-5 | `app/error.tsx` | エラーUI（Error Boundary） |
| 8-6 | `app/tasks/[id]/page.tsx` | タスク詳細・編集ページ |

### Phase 9: Frontend features

| # | ファイル | 内容 |
|---|---------|------|
| 9-1 | `features/tasks/types/index.ts` | 型定義（openapi-typescript生成後に置換） |
| 9-2 | `features/tasks/api/useTasks.ts` | TanStack Query Hooks（CRUD操作） |
| 9-3 | `features/tasks/stores/taskFilterStore.ts` | Zustandフィルターstore |
| 9-4 | `features/tasks/components/TaskCard.tsx` | タスクカードUI |
| 9-5 | `features/tasks/components/TaskList.tsx` | タスク一覧UI |
| 9-6 | `features/tasks/components/TaskForm.tsx` | タスクフォーム（React Hook Form + Zod） |
| 9-7 | `features/tasks/components/TaskFilter.tsx` | フィルターUI |

### Phase 10: Quality / Git hooks

| # | ファイル | 内容 |
|---|---------|------|
| 10-1 | `commitlint.config.js` | Conventional Commits設定 |
| 10-2 | `frontend/.lintstagedrc.json` | lint-staged設定 |
| 10-3 | `frontend/.husky/pre-commit` | pre-commitフック（lint-staged） |
| 10-4 | `frontend/.husky/commit-msg` | commit-msgフック（commitlint） |
| 10-5 | `backend/.pre-commit-config.yaml` | pre-commit設定（Ruff・pyright・alembic check） |

---

## コメントポリシー

### 共通
- 各ファイルの先頭にそのファイルの役割をコメントで明記する
- 型を `any` で誤魔化さない

### Backend（詳細コメント必須）

学習用プロジェクトのため、バックエンドのコメントは通常より大幅に詳細に記載する。以下の観点を必ず含める:

- **FastAPI固有の仕組み**: `Depends` の動作原理、`lifespan` の用途
- **SQLAlchemy固有の挙動**: `AsyncSession` のスコープ、`selectinload` が必要な理由
- **Pydanticの役割**: Request/Response スキーマを分ける理由
- **Pythonの非同期処理**: `async def` vs `def`、`await` が必要な理由
- **設計上の意図**: crud層を分ける理由、DIを使う理由

---

## デプロイ方針（暫定）

現時点では対応不要。後からデプロイしやすいよう意識して実装する。

| 対象 | サービス |
|------|---------|
| FE（Next.js） | Vercel |
| BE（FastAPI） | Render |
| DB（PostgreSQL） | RenderのマネージドPostgreSQL |

**実装上の注意点:**
- 環境変数で設定を外出しする（DB URL・CORSオリジン等をハードコードしない）
- `backend/Dockerfile` を用意する（Renderのコンテナデプロイ用）
- フロントエンドのAPIエンドポイントは `NEXT_PUBLIC_API_URL` 環境変数で切り替え可能にする

---

## 補足

- バックエンドの動作確認は `http://localhost:8000/docs`（Swagger UI）
- フロントエンドの開発サーバーは `http://localhost:3000`
- 判断が必要な箇所は省略せず最もシンプルな実装を選ぶ（学習目的）
- APIクライアントとして Bruno（Postman代替）を推奨。コレクションは `bruno/` で管理
