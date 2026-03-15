# Render等のコンテナデプロイ用Dockerfile
FROM python:3.12-slim

WORKDIR /app

# uv をインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係のインストール
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# アプリケーションコードをコピー
COPY . .

# 非rootユーザーを作成（セキュリティベストプラクティス）
RUN adduser --disabled-password --gecos "" --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Alembicマイグレーション実行後にuvicornで起動
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
