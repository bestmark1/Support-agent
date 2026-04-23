# Repo Refresh And Forkflow Adoption

## Problem

The GitHub repository drifted behind the live VPS workspace.

The live project already includes Telegram runtime code, new migrations, new docs, and runtime scripts that are not represented in the public repository baseline.

This drift makes future changes unsafe because implementation, review, and deployment no longer share one source of truth.

## Scope

- refresh the repository baseline from the live VPS workspace
- exclude secrets and generated runtime artifacts
- add a lightweight workflow standard for future changes
- create a reusable task template for subsequent work

## Non-Goals

- fixing the current Telegram listener behavior in this task
- redesigning the full architecture
- introducing a heavy external ticketing system
- cleaning all historical code and docs in one pass

## Risks

- accidentally committing secrets or session files
- importing host-specific runtime debris into the repository
- normalizing an outdated runtime path by mistake
- mixing repo refresh with unrelated production fixes

## Acceptance Checks

- [x] repository content matches the current live workspace, excluding secrets and generated files
- [x] workflow document exists in `docs/FORKFLOW-LIGHT.md`
- [x] task template exists in `docs/tasks/TEMPLATE.md`
- [x] this task file records the baseline refresh
- [ ] repository baseline can be committed and pushed cleanly

## Implementation Notes

Source of truth for refresh:

- live runtime workspace: `/opt/agent/workspace/fitmentor-agent`

Excluded from sync:

- `.env`
- `.venv/`
- `.secrets/`
- `__pycache__/`
- `*.pyc`
- `*.session`
- `*.egg-info/`
- temporary HTML artifacts

Observed project reality before refresh:

- GitHub `main` had only the early scaffold history
- live workspace contained Telegram runtime, bridge scripts, runbooks, extra migrations, and support summary endpoints
- production listener was running outside the stale repo baseline

## Deploy Plan

This task does not deploy application logic.

It updates the repository baseline so future implementation can happen against the real project state.

## Rollback

- revert the sync commit if sensitive or incorrect files were included
- keep live VPS runtime unchanged during this repository-only task

## Verification

- Status: local sync and pre-commit verification passed; push pending
- Evidence:
  - live workspace staged locally before sync
  - sync excluded `.env`, `.secrets`, `.venv`, session artifacts, and generated files
  - local clone matches the staged live workspace after content-based sync
  - `git diff --check` passed
  - `python3 -m compileall packages services scripts` passed
  - tracked tree contains no `.env`, `.secrets`, or `*.session` files

## Follow-Ups

- fix the listener error and reply-loop behavior under a separate task file
- remove embedded credentials from any host-side git remote configuration
- add a minimal smoke-test script for support flow and KB bridge
