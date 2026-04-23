# FitMentor Agent

Monorepo for the FitMentor autonomous support agent.

## Services

- `kb_api`: knowledge retrieval and write-safe update proposal API
- `telegram_adapter`: real-user Telegram transport and support flow
- `partnership_research`: channel discovery and lead scoring
- `telegram_outreach_search.py`: Telegram discovery script for outreach shortlist building

## Local Setup

1. Copy `.env.example` to `.env`.
2. Fill in database, embedding, and optional gateway settings.
3. Start local infra with Docker Compose.
4. Apply SQL from `migrations/`.
5. Start `kb_api`.

### Quick Start

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0001_init.sql
docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0002_seed_approved_knowledge.sql
curl http://127.0.0.1:8010/kb/health
```

Or use:

```bash
make up
make migrate
make seed
make backfill-embeddings
make health
```

## Runtime Notes

The repository contains both the support data plane and the Telegram-facing runtime pieces used on the VPS.

Key runtime documents:

- `docs/ARCHITECTURE.md`
- `docs/OPENCRABS-RUNBOOK.md`
- `docs/TELEGRAM-AGENT-IMPLEMENTATION-PLAN.md`
- `docs/IDENTITY.md`

## Retrieval

`kb_api` now supports two search modes:

- vector search through `knowledge_embeddings` when embedding credentials are configured
- fallback keyword search through `ILIKE` when embeddings are not configured yet

To fill `knowledge_embeddings` for approved records:

```bash
make backfill-embeddings
```

## Safe Write Path

The agent layer does not write directly into approved knowledge.

Unknown questions go through:

- `POST /kb/proposed-updates`
- stored in `proposed_updates`
- reviewed later by a human

## Support Logging

Support traffic is logged through `kb_api`, not by direct table access from the agent runtime.

The current flow uses:

- `POST /kb/support-threads`
- `POST /kb/support-messages`
- `GET /kb/search`

## Telegram Outreach V1

The repository now includes a first-pass Telegram outreach discovery script:

```bash
env PYTHONPATH=/opt/agent/workspace/fitmentor-agent python /opt/agent/workspace/fitmentor-agent/scripts/telegram_outreach_search.py
```

See:

- [docs/TELEGRAM-OUTREACH-V1.md](docs/TELEGRAM-OUTREACH-V1.md)

## Workflow

This project uses a lightweight task workflow for any non-trivial change.

- `docs/FORKFLOW-LIGHT.md`: project workflow and release gates
- `docs/tasks/TEMPLATE.md`: task artifact template
- `docs/tasks/2026-04-23-repo-refresh-and-forkflow-adoption.md`: first recorded task using the workflow

## CI

GitHub Actions runs the smoke checks on every `push` and `pull_request`.

Local equivalent:

```bash
make test-smoke
```
