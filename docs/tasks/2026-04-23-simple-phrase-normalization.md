# Simple Phrase Normalization

## Problem

After the listener loop fix, an end-to-end smoke message `Привет.` received a low-quality fallback reply instead of a normal greeting.

The support flow already had greeting, thanks, and goodbye branches, but they required exact string matches without terminal punctuation.

## Scope

- normalize simple short phrases with trailing punctuation
- improve greeting, thanks, and goodbye handling
- keep all higher-risk support logic unchanged

## Non-Goals

- redesigning the support reply system
- changing KB retrieval behavior
- changing payment or subscription diagnosis logic

## Risks

- broadening normalization too much and affecting other intent checks
- mixing this copy-quality fix with unrelated support changes

## Acceptance Checks

- [x] `Привет.` returns the greeting branch
- [x] `Спасибо!` returns the thanks branch
- [x] `Bye.` returns the goodbye branch
- [x] deployed listener uses the updated support flow

## Implementation Notes

Fix shape:

- add `_normalized_simple_phrase()`
- use it for greeting checks
- use it for thanks and goodbye checks

## Deploy Plan

- update `services/telegram_adapter/app/support_flow.py` on the VPS
- restart `fitmentor-telegram-listener.service`
- send one short inbound smoke message

## Rollback

- restore the previous `support_flow.py`
- restart `fitmentor-telegram-listener.service`

## Verification

- Status: complete
- Evidence:
  - `python3 -m compileall services/telegram_adapter/app/support_flow.py` passed
  - isolated function check passed for `Привет.`, `Спасибо!`, and `Bye.`
  - fix commit: `b35f4d7`
  - deployed file: `/opt/agent/workspace/fitmentor-agent/services/telegram_adapter/app/support_flow.py`
  - service restart time: `2026-04-23 08:23:49 UTC`
  - real inbound smoke at `2026-04-23T08:24:32+00:00` produced reply: `Здравствуйте. Чем могу помочь вам по FitMentor?`
  - `support-summary` marks the thread as `resolved` with `resolution_note = Automatically resolved by support flow.`

## Follow-Ups

- add a tiny automated smoke test for simple conversational phrases
