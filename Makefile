.PHONY: up down be fe migrate gen-api lint test

up:
	podman-compose up -d

down:
	podman-compose down

be:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

fe:
	cd frontend && npm run dev

migrate:
	cd backend && uv run alembic upgrade head

gen-api:
	cd frontend && npm run gen:api

lint:
	cd backend && uv run ruff check .
	cd frontend && npm run lint

test:
	cd backend && uv run pytest
