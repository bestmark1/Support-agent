# Light Operator Actions

## Problem

Conversational operator mode is good for reading support state, but there is still friction for simple owner actions.

Typical examples:

- close the latest case
- return the latest case to `manual_review`
- show the latest case ID without digging through summaries

## Scope

- keep natural-language operator mode
- add lightweight action intents instead of a strict slash-command system
- support:
  - close latest case
  - return latest case to `manual_review`
  - show latest case ID

## Non-Goals

- building a full command framework
- adding arbitrary thread mutations by free-form text
- changing end-user support flow

## Risks

- ambiguous phrasing could trigger an operator action unexpectedly
- action selection could target the wrong latest case if summary ordering is misunderstood

## Acceptance Checks

- [ ] operator phrases for close / reopen / show ID are recognized
- [ ] latest actionable case is selected from current support summary
- [ ] local smoke suite passes
- [ ] deploy keeps listener healthy

## Verification

- Status: pending

## Rollback

- restore previous `services/telegram_adapter/app/support_flow.py`
- restart `fitmentor-telegram-listener.service`
