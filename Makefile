.PHONY: up down logs migrate seed schemas

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec api-service alembic -c sql/migrations/alembic.ini upgrade head

seed:
	docker compose exec postgres psql -U tradechain -d tradechain -f /workspace/sql/seeds/001_skill_versions.sql

schemas:
	PYTHONPATH=. python scripts/export_contract_schemas.py
