# Local Setup

## What This Gives You

Local Docker runtime for:

- `postgres` with `pgvector`
- `kb_api` on `http://127.0.0.1:8010`

This is enough to:

- create the base schema
- test the API health endpoint
- test the future retrieval layer

## Start

```bash
cp .env.example .env
docker compose up --build -d
```

## Apply Migration

```bash
docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0001_init.sql
```

## Check Health

```bash
curl http://127.0.0.1:8010/kb/health
```

Expected response:

```json
{"status":"ok"}
```

## Seed Initial Knowledge

```bash
docker compose exec -T postgres psql -U postgres -d fitmentor < migrations/0002_seed_approved_knowledge.sql
```

Or:

```bash
make seed
```

This inserts the first approved records for:

- product overview
- basic FAQ
- support policy boundary
- support tone

## Backfill Embeddings

After embedding settings are configured in `.env`, run:

```bash
make backfill-embeddings
```

This will:

- read approved records from `knowledge_base`
- generate embeddings for records that do not have vectors yet
- upsert rows into `knowledge_embeddings`

## Retrieval Mode

Right now `kb_api` supports:

- vector search if `EMBEDDING_API_KEY` is configured and `knowledge_embeddings` contains vectors
- fallback text search if embeddings are not configured yet

To fully enable semantic search, the next step is to add an embedding backfill job for approved knowledge records.

## Stop

```bash
docker compose down
```

## Notes

- `kb_api` uses `DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/fitmentor`
- Telegram transport is not part of this local step
