# Listener Loop Guard

## Problem

The Telegram listener processes messages from the real-user account and can re-handle its own replies.

On April 23, 2026, the journal showed a repeated reply chain where support replies triggered new support handling again:

- message ids progressed as `1533 -> 1535 -> 1536 -> ...`
- each auto-reply produced another auto-reply
- the listener also emitted repeated `listener_error` records with an empty error string

This makes the live support loop unsafe.

## Scope

- stop the listener from processing self-authored or outgoing messages
- improve `listener_error` logging so the next failure is diagnosable
- keep the support flow behavior unchanged for real inbound user messages

## Non-Goals

- redesigning the whole support flow
- changing KB retrieval logic
- changing operator command behavior
- deploying unrelated cleanup

## Risks

- ignoring legitimate inbound events by using an over-broad filter
- fixing the loop in the listener while leaving another live entrypoint unchanged
- deploying without a clear before/after smoke check

## Acceptance Checks

- [x] self-authored or outgoing listener events are ignored
- [x] listener still processes real inbound user messages
- [x] listener errors include exception type and traceback
- [x] syntax verification passes

## Implementation Notes

Observed evidence before the fix:

- support account id on VPS: `7448513035`
- listener journal showed repeated support replies with `sent_message.sender_id = 7448513035`
- the next processed support event kept using the freshly sent reply as a new inbound support message

Fix shape:

- add a listener-level guard for `message.out`
- add a listener-level guard for `sender_id == self_user_id`
- keep the fix at the runtime entrypoint to avoid widening unrelated behavior

## Deploy Plan

- update `scripts/support_listener.py` on the VPS
- restart `fitmentor-telegram-listener.service`
- inspect recent journal entries
- run one controlled Telegram smoke message

## Rollback

- restore the previous script version from git
- restart `fitmentor-telegram-listener.service`

## Verification

- Status: complete
- Evidence:
  - live journal captured the reply loop and blank `listener_error`
  - self account id was confirmed directly on the VPS
  - `python3 -m compileall scripts/support_listener.py` passed
  - local guard smoke passed for self-authored, outgoing, and real inbound cases
  - fix commit: `a5fea45`
  - deployed file: `/opt/agent/workspace/fitmentor-agent/scripts/support_listener.py`
  - service restart time: `2026-04-23 08:10:53 UTC`
  - post-restart journal shows `listener_started` and no immediate repeated `listener_error`
  - real inbound smoke at `2026-04-23T08:21:08+00:00` produced exactly one support handling event for `message_id=1564`
  - that smoke produced exactly one outbound reply `message_id=1565`, with no follow-up loop
  - direct self-message smoke from a second Telethon process was blocked by `sqlite3.OperationalError: database is locked`

## Follow-Ups

- if another entrypoint can feed self-authored messages into `process_support_message`, add the same guard there
- monitor the next few live support events for hidden duplicate-processing paths
