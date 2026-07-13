.PHONY: dev build down migrate test lint clean

dev:
	docker compose -f docker/docker-compose.yml up --build

build:
	docker compose -f docker/docker-compose.yml build

down:
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f

migrate:
	docker compose -f docker/docker-compose.yml exec api alembic upgrade head

migrate-create:
	docker compose -f docker/docker-compose.yml exec api alembic revision --autogenerate -m "$(name)"

test-api:
	docker compose -f docker/docker-compose.yml exec api pytest

test-web:
	docker compose -f docker/docker-compose.yml exec web npm test

lint:
	docker compose -f docker/docker-compose.yml exec api ruff check .
	docker compose -f docker/docker-compose.yml exec api mypy .

clean:
	docker compose -f docker/docker-compose.yml down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

shell-api:
	docker compose -f docker/docker-compose.yml exec api bash

shell-web:
	docker compose -f docker/docker-compose.yml exec web sh
