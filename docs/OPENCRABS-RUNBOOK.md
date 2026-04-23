# OpenCrabs Runbook

## Purpose

Short index for the real runtime paths, services, and recovery commands used in the current FitMentor + OpenCrabs setup.

Read this first before touching `tools.toml`, `kb_api`, or Docker.

## Related Docs

- [OPENCRABS-INTEGRATION.md](./OPENCRABS-INTEGRATION.md)
- [OPENCRABS-TOOLS.md](./OPENCRABS-TOOLS.md)
- [LOCAL-SETUP.md](./LOCAL-SETUP.md)

## Runtime Paths

### Host Paths

- OpenCrabs binary: `/opt/agent/workspace/opencrabs-bin/opencrabs`
- OpenCrabs home: `/opt/agent/workspace/opencrabs-home/.opencrabs`
- OpenCrabs config: `/opt/agent/workspace/opencrabs-home/.opencrabs/config.toml`
- OpenCrabs tools: `/opt/agent/workspace/opencrabs-home/.opencrabs/tools.toml`
- FitMentor repo: `/opt/agent/workspace/fitmentor-agent`
- Bridge script: `/opt/agent/workspace/fitmentor-agent/scripts/opencrabs_kb_bridge.py`

### Container-Only Paths

These are valid inside the Codex workspace container, not in the host root shell:

- `/workspace/opencrabs`
- `/workspace/opencrabs-home/.opencrabs`
- `/workspace/fitmentor-agent`

Do not use `/workspace/...` paths from the host shell unless you first confirm they exist there.

## Service Names

### Docker Compose Services

- `postgres`
- `kb_api`

### Container Names

- `fitmentor-postgres`
- `fitmentor-kb-api`
- `codex-agent`

## Current Integration Shape

OpenCrabs should call a narrow local bridge, not the database directly.

Current bridge entrypoint:

- `python3 /opt/agent/workspace/fitmentor-agent/scripts/opencrabs_kb_bridge.py`

Supported bridge commands:

- `search_knowledge`
- `create_proposed_update`
- `ensure_support_thread`
- `log_support_message`

## OpenCrabs tools.toml Rule

On the host, `tools.toml` must use:

```toml
python3 /opt/agent/workspace/fitmentor-agent/scripts/opencrabs_kb_bridge.py ...
```

Do not use:

```toml
python3 /workspace/fitmentor-agent/scripts/opencrabs_kb_bridge.py ...
```

unless you are inside the workspace container and have confirmed that path exists there.

## Health Checks

### kb_api

```bash
curl -i http://127.0.0.1:8010/kb/health
curl -i 'http://127.0.0.1:8010/kb/search?query=test&limit=3'
```

Expected search result after schema init:

```json
{"items":[],"query":"test","limit":3}
```

### Bridge

```bash
printf '%s\n' '{"query":"test","limit":3}' | python3 /opt/agent/workspace/fitmentor-agent/scripts/opencrabs_kb_bridge.py search_knowledge
```

Expected:

```json
{"ok": true, "result": {"items": [], "query": "test", "limit": 3}}
```

## Database Recovery

If Postgres volume is reset, reapply schema before testing `kb_api` search:

```bash
docker compose -f /opt/agent/workspace/fitmentor-agent/docker-compose.yml exec -T postgres psql -U postgres -d fitmentor < /opt/agent/workspace/fitmentor-agent/migrations/0001_init.sql
```

Optional seed data:

```bash
docker compose -f /opt/agent/workspace/fitmentor-agent/docker-compose.yml exec -T postgres psql -U postgres -d fitmentor < /opt/agent/workspace/fitmentor-agent/migrations/0002_seed_approved_knowledge.sql
```

## Compose Facts

Current repo config expects:

- `POSTGRES_DB=fitmentor`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/fitmentor`

Postgres password drift note:

- the support stack forces `postgres/postgres` as the canonical local credential pair
- `docker/postgres-start.sh` re-applies `ALTER USER postgres WITH PASSWORD 'postgres'` on each container start
- this avoids the common Postgres-volume drift where `POSTGRES_PASSWORD` in compose no longer matches the real password stored inside an older volume

If `kb_api` returns `500`, check:

```bash
docker logs --tail 120 fitmentor-kb-api
docker logs --tail 120 fitmentor-postgres
```

## Common Failure Modes

### `relation "knowledge_embeddings" does not exist`

Cause: schema was not initialized after recreating the Postgres volume.

Fix: apply `migrations/0001_init.sql`.

### `Temporary failure in name resolution`

Cause: `kb_api` cannot resolve the Postgres host inside Docker, usually because Postgres is not up or the container/network is broken.

Fix: inspect `fitmentor-postgres`, then recreate the Postgres container and volume if needed.

### `No such file or directory` for bridge path

Cause: using container path `/workspace/...` from the host shell.

Fix: use `/opt/agent/workspace/...`.

### `OpenCrabs tools.toml` not found

Cause: checking container path from host.

Fix: use `/opt/agent/workspace/opencrabs-home/.opencrabs/tools.toml`.

## Next Step Checklist

1. Confirm `kb_api` health and search both return `200`.
2. Confirm bridge returns `"ok": true`.
3. Confirm `/opt/agent/workspace/opencrabs-home/.opencrabs/tools.toml` uses host bridge paths.
4. Start or restart OpenCrabs.
5. Smoke test from OpenCrabs runtime.
