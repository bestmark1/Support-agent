# VPS Workspace Normalization

## Problem

The live VPS workspace drifted away from GitHub again.

Observed state before cleanup:

- live workspace branch: `main` at old commit `c760f43`
- current GitHub `main` already contains the real runtime code and fixes
- live workspace still held those newer files as a mix of tracked modifications and untracked runtime code
- git remote on the VPS still used an embedded GitHub PAT

That means the VPS workspace was not a safe source for future `git pull` or review-based deployment.

## Scope

- normalize the VPS workspace so the repository becomes the source of truth again
- preserve required runtime artifacts:
  - `.env`
  - `.secrets/`
  - `.venv/`
- replace the drifted workspace with a fresh clone from GitHub
- ensure the git remote no longer contains an embedded PAT

## Non-Goals

- rebuilding Docker images
- changing the support listener service definition
- changing Telegram session contents

## Risks

- interrupting the listener during workspace replacement
- losing required local runtime artifacts
- preserving an outdated venv or env state that should be reviewed later

## Acceptance Checks

- [x] VPS workspace `HEAD` matches current GitHub `main`
- [x] `git status --short` is clean after normalization
- [x] `origin` remote is clean and PAT-free
- [x] listener service is running after normalization
- [x] `kb_api` health still returns `ok`

## Implementation Notes

Safe approach:

1. stop the listener
2. move the old workspace aside as a timestamped backup
3. clone a fresh repo to the original path
4. restore `.env`, `.secrets`, and `.venv`
5. restart the listener
6. verify git state and runtime health

## Deploy Plan

This task changes the live workspace layout on the VPS.

Verification must include:

- `git status`
- `git rev-parse HEAD`
- `git remote -v`
- `systemctl status fitmentor-telegram-listener`
- `curl http://127.0.0.1:8010/kb/health`

## Rollback

- stop the listener
- move the fresh clone aside
- restore the timestamped pre-normalization workspace to the original path
- restart the listener

## Verification

- Status: complete
- Evidence:
  - backup workspace created: `/opt/agent/workspace/fitmentor-agent.pre-normalize-20260423T083331Z`
  - normalized workspace `HEAD`: `f8e8a050aa4c5aa89e3c5087a457c0ade1fa5039`
  - normalized branch: `main` tracking `origin/main`
  - `git status --short` is empty after normalization
  - `origin` remote is `https://github.com/bestmark1/Support-agent.git`
  - listener restart time: `2026-04-23 08:33:33 UTC`
  - `fitmentor-telegram-listener.service` returned to `active (running)`
  - `curl http://127.0.0.1:8010/kb/health` returned `{"status":"ok"}`

## Follow-Ups

- decide whether to keep the old workspace backup after a cooling-off period
- document the standard VPS update path if the new layout proves stable
