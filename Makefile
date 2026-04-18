up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f kb_api

migrate:
	docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0001_init.sql
	docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0003_vector_index.sql

seed:
	docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0002_seed_approved_knowledge.sql
	docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0004_seed_support_cases.sql

backfill-embeddings:
	docker compose exec kb_api python -m services.kb_api.app.backfill_embeddings

health:
	curl -s http://127.0.0.1:8010/kb/health
