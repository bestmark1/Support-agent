# Forkflow Light

Lightweight delivery workflow for the FitMentor support agent.

Use this for any change that touches support behavior, Telegram runtime, KB schema, bridge tools, or deployment.

## Why This Exists

This project already runs a live Telegram-facing support flow on the VPS.

That means small code changes can affect:

- real user replies
- support audit logs
- KB update proposals
- OpenCrabs tool behavior
- `systemd` and Docker runtime state

The goal is not ceremony. The goal is to keep scope small, make checks repeatable, and leave rollback evidence behind.

## When To Use The Full Light Flow

Use the full flow when the change affects:

- `services/telegram_adapter`
- `scripts/support_listener.py`
- `scripts/opencrabs_*`
- `services/kb_api`
- `migrations/`
- `docker-compose.yml`
- `docs/FITMENTOR-TELEGRAM-LISTENER.service`

Use a shortened flow for low-risk doc edits or tiny internal refactors.

## Flow

### 1. Trigger

Start from a bug, request, user report, prod incident, or operator need.

Record one task file under `docs/tasks/`.

### 2. Explore

Before changing code, inspect:

- the runtime path that is actually in use
- the current docs and runbook
- the current logs or failing evidence
- related schema or tool contracts

Do not implement from memory.

### 3. Clarify

Write down in the task file:

- problem
- scope
- non-goals
- risks
- acceptance checks
- rollback

If the task is not trivial, freeze this before implementation.

### 4. Implement

Make the smallest change that solves the stated problem.

Rules:

- no scope creep
- no unrelated cleanup in the same commit
- no direct writes to approved knowledge
- keep support, research, and publishing behavior separated

### 5. Local Checks

Run the smallest relevant checks before deploy.

Minimum check menu:

- `curl http://127.0.0.1:8010/kb/health`
- `curl 'http://127.0.0.1:8010/kb/support-summary?days=1&include_tests=true'`
- KB bridge smoke test
- support loop smoke test when reply logic changed
- migration or schema verification when SQL changed

If a check is skipped, write why in the task file.

### 6. Review

For risky changes, do a focused adversarial review of:

- reply loops
- duplicate sends
- logging correctness
- manual-review escalation
- migration safety
- rollback path

### 7. Deploy

Deploy only the files needed for the task.

Do not mix deployment with unrelated repo cleanup.

### 8. Prod Verification

After deploy, record:

- exact commit hash
- services restarted
- health check result
- one end-to-end smoke result
- whether rollback is still available

### 9. Evidence

Append the outcome to the task file:

- verification status
- known findings
- follow-ups
- rollback notes

## Required Artifact

Each non-trivial task should have one file in `docs/tasks/`.

That file is the source of truth for:

- intent
- scope
- checks
- deploy evidence

## Minimum Gates By Change Type

### Support Logic

Required:

- task file
- support smoke check
- prod verification

### Schema Or API Contract

Required:

- task file
- migration note
- example request or response
- rollback note

### Runtime Or Deployment

Required:

- task file
- service restart note
- health check
- rollback command

### Docs-Only

Required:

- task file only if the doc changes operational behavior

## Anti-Patterns

Do not do these:

- change prod behavior without a task artifact
- deploy code that is not committed
- push runtime-only experiments without documenting them
- mix support and outreach changes in one task
- leave manual-review behavior unverified after reply changes
- rely on "I checked it in my head"
