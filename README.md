# FitMentor Agent

Monorepo for the FitMentor autonomous support agent.

## Services

- `support_agent`: Telegram support workflow
- `kb_api`: knowledge retrieval and write-safe update proposal API
- `partnership_research`: channel discovery and lead scoring

## Local Setup

1. Copy `.env.example` to `.env`.
2. Fill in Supabase, AI gateway, and Telegram credentials.
3. Start local infra with Docker Compose.
4. Apply SQL from `migrations/`.
5. Start `kb_api`.
6. Start `support_agent`.

### Quick Start

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0001_init.sql
docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0002_seed_approved_knowledge.sql
curl http://127.0.0.1:8000/kb/health
```

Or use:

```bash
make up
make migrate
make seed
make backfill-embeddings
make health
```

To start the support runtime after `.env` is configured:

```bash
docker compose up --build -d support_agent
docker compose logs -f support_agent
```

## Current Status

This repository contains the initial scaffold and first database migration.

## Retrieval

`kb_api` now supports two search modes:

- vector search through `knowledge_embeddings` when embedding credentials are configured
- fallback keyword search through `ILIKE` when embeddings are not configured yet

To fill `knowledge_embeddings` for approved records:

```bash
make backfill-embeddings
```

## Safe Write Path

`support_agent` does not write directly into approved knowledge.

Unknown questions go through:

- `POST /kb/proposed-updates`
- stored in `proposed_updates`
- reviewed later by a human

## Support Logging

Support traffic is logged through `kb_api`, not by direct table access from the bot runtime.

The current flow uses:

- `POST /kb/support-threads`
- `POST /kb/support-messages`
- `GET /kb/search`
