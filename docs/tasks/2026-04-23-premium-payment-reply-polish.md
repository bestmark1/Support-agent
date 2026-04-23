# Premium And Payment Reply Polish

## Problem

The highest-value live support bucket is still `premium_entitlement`, and the related payment/access replies are correct but too internal and stiff.

Examples of weak phrasing:

- `обновление Premium-прав`
- `доступ ещё не применился`
- generally technical wording where a normal support phrasing would be clearer

## Scope

- polish reply wording for:
  - `premium_entitlement`
  - `subscription_activation_issue`
  - `payment_failed`
- keep the underlying routing and confidence rules unchanged
- add smoke coverage for the polished wording

## Non-Goals

- changing support diagnosis logic
- rewriting all support replies at once
- changing database status handling

## Risks

- making replies friendlier but less precise
- accidentally changing branch selection instead of just text quality

## Acceptance Checks

- [x] `premium_entitlement` reply uses human wording
- [x] `subscription_activation_issue` manual-check reply is clearer
- [x] `payment_failed` reply sounds more practical
- [x] smoke tests cover the updated wording
- [x] local smoke suite passes

## Implementation Notes

This task changes copy only.

The goal is:

- shorter phrasing
- less internal terminology
- more natural support voice

## Deploy Plan

- update `services/telegram_adapter/app/support_flow.py` on the VPS
- restart `fitmentor-telegram-listener.service`

## Rollback

- restore the previous `support_flow.py`
- restart `fitmentor-telegram-listener.service`

## Verification

- Status: local verification passed; deploy pending
- Evidence:
  - `make test-smoke` passed locally with 10 tests
  - `python3 -m compileall services/telegram_adapter/app/support_flow.py tests/test_support_flow_smoke.py` passed
  - `premium_entitlement` wording no longer uses `Premium-прав`
  - payment/access manual-check replies now use clearer support phrasing
  - refined `premium_entitlement` active-Premium reply to ask which exact limit or feature did not update after payment
  - smoke test now checks for the clarification prompt instead of a generic manual-review sentence
  - added specific follow-up handling for `AI message limit did not update` after Premium payment
  - smoke suite now covers both generic Premium clarification and the AI-limit-specific follow-up reply

## Follow-Ups

- polish refund and duplicate-charge replies if those cases start appearing more often
