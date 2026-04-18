# Architecture Notes

## Support Flow

1. Receive Telegram message.
2. `OpenCrabs` searches approved knowledge through `kb_api`.
3. `OpenCrabs` decides on the answer using `Codex OAuth`.
4. `kb_api` stores logs and `proposed_updates`.

## Safe Update Flow

1. Support cannot modify `knowledge_base`.
2. Support can only submit a proposal into `proposed_updates`.
3. Approved knowledge is updated only after human review.

## Support Logging Flow

1. `OpenCrabs` ensures a thread through `kb_api`.
2. User message is logged through `kb_api`.
3. Knowledge is fetched through `kb_api`.
4. Assistant reply is logged through `kb_api`.

## Partnership Flow

1. Add or discover a lead.
2. Score the lead.
3. Review manually.
4. Decide whether to contact.
