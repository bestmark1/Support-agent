# Task: Fix internal subscription-check integration

## Problem

Support-agent called `https://fitmentor-ai.ru/api/internal/support/subscription-check`, but the public domain returned `404` through an external Caddy layer even after the endpoint was added to FitMentor `webapp`.

## Scope

- Add missing `/api/internal/support/subscription-check` route to FitMentor `webapp`.
- Protect the route with `X-Support-Token`.
- Switch support-agent internal base URL from public domain to local `http://127.0.0.1:8000`.
- Verify both direct endpoint responses and support-agent runtime calls.

## Non-goals

- Rework external reverse proxy configuration outside this VPS.
- Add payment-pending diagnostics beyond current subscription state.

## Risks

- If `webapp` is not recreated, the new route and token config will not load.
- If support-agent keeps the public domain, the old `404` path remains.

## Acceptance checks

- `curl http://127.0.0.1:8000/health` returns `{"status":"ok","database":"ok"}`.
- Local POST to `/api/internal/support/subscription-check` with support token returns `200`.
- Query for an active Premium user returns `diagnosis=subscription_active`.
- Query from support-agent runtime no longer raises `404`.

## Deploy

- Rebuild and recreate `fitmentor_webapp`.
- Update `/opt/agent/workspace/fitmentor-agent/.env`.
- Restart `fitmentor-telegram-listener.service`.

## Evidence

- `fitmentor_webapp` recreated successfully and healthy.
- Direct `curl` to `127.0.0.1:8000` returned both `no_payment_found` and `subscription_active`.
- Listener runtime check succeeded after base URL switch.
