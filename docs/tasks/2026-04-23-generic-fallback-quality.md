# Generic Fallback Quality

## Problem

The default fallback reply was too payment-centric even for generic unknown support messages.

That caused low-quality behavior such as answering `Привет.` or other non-payment unknowns with a request for payment date, amount, and confirmation.

## Scope

- split the default fallback into:
  - payment or access context
  - general unknown support context
- keep existing explicit payment, subscription, and premium branches unchanged
- add smoke coverage for the new fallback split

## Non-Goals

- redesigning all support copy
- changing KB search behavior
- changing manual-review persistence rules

## Risks

- making generic fallback too vague
- accidentally weakening the payment-oriented path for real billing cases

## Acceptance Checks

- [x] generic unknown message gets a neutral clarification fallback
- [x] payment-related unknown message stays payment-oriented
- [x] smoke tests cover both branches
- [x] local smoke suite passes

## Implementation Notes

Fix shape:

- add `_is_payment_or_access_context()`
- keep explicit issue handlers first
- use a neutral fallback only when no payment or access context is detected

## Deploy Plan

- update `services/telegram_adapter/app/support_flow.py` on the VPS
- restart `fitmentor-telegram-listener.service`
- send one generic smoke message if needed

## Rollback

- restore the previous `support_flow.py`
- restart `fitmentor-telegram-listener.service`

## Verification

- Status: local verification passed; deploy pending
- Evidence:
  - `make test-smoke` passed locally with 8 tests
  - `python3 -m compileall services/telegram_adapter/app/support_flow.py tests/test_support_flow_smoke.py` passed
  - generic unknown case now gets a neutral clarification fallback
  - payment-like case keeps the payment-oriented reply

## Follow-Ups

- consider adding a separate fallback for product-usage questions if they recur
