# Architecture Notes

## Support Flow

1. Receive Telegram message.
2. Search approved knowledge.
3. Assemble prompt context.
4. Call AI gateway.
5. Reply.
6. If needed, create `proposed_updates`.

## Safe Update Flow

1. Support cannot modify `knowledge_base`.
2. Support can only submit a proposal into `proposed_updates`.
3. Approved knowledge is updated only after human review.

## Support Logging Flow

1. `support_agent` ensures a thread through `kb_api`.
2. User message is logged through `kb_api`.
3. Knowledge is fetched through `kb_api`.
4. Assistant reply is logged through `kb_api`.

## Partnership Flow

1. Add or discover a lead.
2. Score the lead.
3. Review manually.
4. Decide whether to contact.
