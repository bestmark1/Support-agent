# Smoke Tests CI

## Problem

The repository already has local smoke tests, but they still depend on someone remembering to run them before push or deploy.

That leaves a simple path for regressions to skip the guardrail.

## Scope

- add a GitHub Actions workflow for smoke tests
- run the smoke suite on `push`
- run the smoke suite on `pull_request`
- document the CI behavior in the repository

## Non-Goals

- full integration CI
- database-backed tests in CI
- deployment automation

## Risks

- introducing a CI workflow that depends on optional local tooling
- making the first CI gate too broad or flaky

## Acceptance Checks

- [x] GitHub Actions workflow exists
- [x] workflow runs `make test-smoke`
- [x] workflow triggers on `push` and `pull_request`
- [x] repository docs mention the CI entrypoint

## Implementation Notes

The first CI gate stays intentionally small:

- no Docker
- no Postgres
- no Telegram runtime
- only the smoke tests that already pass locally

## Deploy Plan

No production deploy required.

The effect is repository-side verification in GitHub.

## Rollback

- remove `.github/workflows/smoke-tests.yml` if the workflow proves noisy or blocks normal development

## Verification

- Status: complete
- Evidence:
  - `.github/workflows/smoke-tests.yml` added
  - `README.md` documents the local CI-equivalent command
  - `make test-smoke` passed locally with 6 tests

## Follow-Ups

- add branch protection after the workflow is stable
- consider a second CI job for syntax or packaging checks if needed
