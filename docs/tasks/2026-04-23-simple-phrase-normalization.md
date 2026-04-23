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
- [ ] deployed listener uses the updated support flow

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

- Status: local verification passed; deploy pending
- Evidence:
  - `python3 -m compileall services/telegram_adapter/app/support_flow.py` passed
  - isolated function check passed for `Привет.`, `Спасибо!`, and `Bye.`

## Follow-Ups

- add a tiny automated smoke test for simple conversational phrases
