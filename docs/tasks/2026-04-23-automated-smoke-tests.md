# Automated Smoke Tests

## Problem

The project caught two production-facing regressions only after live smoke:

- the listener self-reply loop
- bad fallback behavior for simple greeting messages like `Привет.`

There was no automated smoke layer to catch these low-cost, high-signal failures before deploy.

## Scope

- add a minimal automated smoke test for listener guards
- add a minimal automated smoke test for simple support replies
- provide a stable local command for running those tests

## Non-Goals

- building a full integration test harness
- provisioning Telegram or Postgres in CI
- rewriting runtime code for testability beyond the smoke surface

## Risks

- overfitting tests to stubbed imports instead of business behavior
- making tests depend on local optional packages like `telethon`

## Acceptance Checks

- [x] listener guard smoke test exists
- [x] support-flow simple-phrase smoke test exists
- [x] tests run with stdlib `unittest`
- [x] `make test-smoke` passes locally

## Implementation Notes

Test strategy:

- use `unittest`
- stub `telethon` modules in-process where runtime SDK is not required
- verify only the narrow behaviors that already caused production regressions

## Deploy Plan

No production deploy required for this task by itself.

The value is pre-deploy verification for future support changes.

## Rollback

- remove the added tests and `Makefile` target if they prove noisy or misleading

## Verification

- Status: complete
- Evidence:
  - `tests/test_listener_guard.py` added
  - `tests/test_support_flow_smoke.py` added
  - `Makefile` includes `test-smoke`
  - `make test-smoke` passed locally with 6 tests

## Follow-Ups

- add a tiny CI step that runs `make test-smoke`
