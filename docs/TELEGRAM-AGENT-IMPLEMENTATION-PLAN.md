# Telegram Agent Implementation Plan

## Goal

Build a Telegram-capable agent stack for FitMentor with three distinct capabilities:

1. real-user Telegram support operations
2. Telegram channel parsing for partnership research
3. optional Telegram channel publishing for FitMentor

The system should use OpenCrabs as the orchestration layer, not as the direct Telegram runtime.

## Current Decisions

These points are already decided and should be treated as the working baseline unless explicitly changed.

- OpenCrabs will remain the orchestration layer, not the Telegram transport layer.
- Real-user Telegram access will use `Telethon`, not the current OpenCrabs Telegram bot channel.
- `kb_api` remains the source of approved knowledge retrieval and support logging.
- OpenCrabs will call narrow tools, not direct database queries.
- Telegram support, Telegram parsing, and Telegram publishing are separate capability groups.
- Publishing should not be autonomous in v1; it should stay approval-gated.
- The first working integration path should be a narrow CLI bridge, not an MCP server.
- The agent identity should live in a dedicated repo document, not in chat memory.

## Current Checkpoint

This is the current verified checkpoint and should be treated as the active baseline.

- `kb_api` is running and `GET /kb/search` returns `200`
- the KB bridge works from the host
- the Telethon adapter works from the host
- the real Telegram support account has been authenticated successfully
- OpenCrabs is running as a `systemd` service on the VPS
- the host `tools.toml` already contains both KB tools and Telegram real-user tools

What is not done yet:

- there is no automated support loop consuming incoming Telegram messages and replying
- OpenCrabs has not yet been wired into a full end-to-end support workflow
- publishing remains unimplemented as an approved workflow
- owner/operator flow is not yet implemented as a human-like personal agent mode
- candidate knowledge review from solved support cases is not yet wired to owner approvals
- candidate knowledge drafts should be based on generalized KB cards, not raw fallback replies
- Premium users should be marked as priority support in runtime handling

This is why writing to the support account from another Telegram account does not yet produce an automatic reply.

## Current Infrastructure State

At the time of writing, the working host-side runtime paths are:

- OpenCrabs binary: `/opt/agent/workspace/opencrabs-bin/opencrabs`
- OpenCrabs home: `/opt/agent/workspace/opencrabs-home/.opencrabs`
- OpenCrabs tools config: `/opt/agent/workspace/opencrabs-home/.opencrabs/tools.toml`
- FitMentor repo: `/opt/agent/workspace/fitmentor-agent`
- Current KB bridge: `/opt/agent/workspace/fitmentor-agent/scripts/opencrabs_kb_bridge.py`

Current Docker components:

- `fitmentor-postgres`
- `fitmentor-kb-api`
- `codex-agent`

Current Compose service names:

- `postgres`
- `kb_api`

Current `kb_api` host endpoints:

- `http://127.0.0.1:8010/kb/health`
- `http://127.0.0.1:8010/kb/search`
- `http://127.0.0.1:8010/kb/proposed-updates`
- `http://127.0.0.1:8010/kb/support-threads`
- `http://127.0.0.1:8010/kb/support-messages`

## Current Working Assumptions

- The support side should answer subscriber questions, including payment and subscription-adjacent issues, through `kb_api` and controlled write paths.
- Partnership research should parse Telegram channels in nutrition, fitness, wellness, and adjacent niches.
- FitMentor channel publishing may be useful, but should begin as human-approved posting, not autonomous posting.
- If text and image are already prepared, manual publishing may remain cheaper than full automation until posting volume justifies more tooling.

## Identity Source

The current source document for the agent identity is:

- `/workspace/fitmentor-agent/docs/IDENTITY.md`

This should be treated as the draft source for any later OpenCrabs identity-file or system-prompt integration.

## Architecture

### Core Rule

Do not force the current OpenCrabs Telegram bot integration to handle real-user Telegram workflows.

Use a separate Telegram adapter built on `Telethon` and expose only narrow tools to OpenCrabs.

### Components

- `OpenCrabs`
  - reasoning
  - orchestration
  - approval flow
  - tool selection

- `kb_api`
  - approved knowledge retrieval
  - support thread logging
  - support message logging
  - proposed updates

- `Telethon adapter`
  - real-user Telegram session
  - message retrieval
  - dialog/channel parsing
  - outbound sending
  - optional publishing

- optional graph memory layer
  - long-term markdown-based graph memory
  - relationship context
  - research notes
  - channel and partnership observations

## Separation Of Responsibilities

### 0. Owner / Operator Flow

Used when the project owner writes to the support account as an operator, not as a normal subscriber.

Examples:

- how many people wrote today
- what payment problems appeared
- what is currently broken
- summarize unresolved support cases
- confirm or reject a candidate knowledge item

This flow should:

- answer in a human-like agent style, not like a canned support bot
- use free-form reasoning over logs, support data, and narrow backend checks
- keep `/support_test` or equivalent as the explicit path for owner-as-test-user support checks
- remain distinct from normal support-user automation
- receive candidate knowledge notifications in personal Telegram with natural-language review

Expected behavior:

- natural-language responses
- no rigid slash-command requirement for owner interaction
- the agent should understand ordinary confirmations such as `подтверждаю`, `не добавляй`, `исправь так: ...`

### 1. Support

Used when subscribed FitMentor users write to the support account.

Examples:

- payment did not go through
- subscription state question
- account-related clarification
- product usage question

This flow should:

- retrieve approved KB data through `kb_api`
- log support threads and messages through `kb_api`
- escalate uncertain answers through `proposed_updates`
- avoid direct database writes from OpenCrabs
- mark Premium users as `priority_support` and surface that priority in owner-facing review/ops flows

### 2. Partnership Parsing

Used to inspect Telegram channels related to nutrition, fitness, wellness, and adjacent niches.

Examples:

- collect channel metadata
- inspect recent posts
- search for collaboration signals
- identify possible outreach targets

This flow should be isolated from support operations and should be callable as a separate tool group.

Expected outputs:

- candidate channel summaries
- channel/topic metadata
- recent post summaries
- collaboration signals
- outreach draft candidates

### 3. Publishing

Used for posting to FitMentor-owned Telegram channels.

Examples:

- scheduled post publication
- approved campaign post publishing
- posting already-prepared text and image

This should be treated as a higher-risk action than reading or drafting.

Expected v1 mode:

- draft inside the agent
- review by human
- publish only after explicit approval

## Security Model

### Strong Recommendation

Keep support, parsing, and publishing as separate capability groups, even if they share the same Telethon runtime.

### Why

- support actions touch real users
- parsing touches external channels and research workflows
- publishing affects public brand output

### Access Pattern

OpenCrabs should not get unrestricted raw Telethon access.

Expose narrow tools only.

## Memory Model

### Current Durable Memory Layers

- `kb_api` + Postgres
  - approved support knowledge
  - support thread identity
  - support message audit log
  - proposed KB updates

- Telegram session state
  - real-user authentication state
  - transport/runtime concern only

### Candidate Additional Memory Layer

`Autograph` is a plausible fit as a second memory layer for long-term graph-like context, but not as a replacement for `kb_api`.

Good uses for an `Autograph`-style graph:

- long-term notes about channels and niches
- partnership lead cards
- organization and contact cards
- recurring collaboration signals
- internal research notes across weeks or months
- draft memory for observations that are too fluid for the approved KB

Bad uses for an `Autograph`-style graph:

- authoritative payment or subscription answers
- support audit logging
- canonical approved knowledge used for user-facing support replies

### Recommended Boundary

- `kb_api` stays authoritative for approved support knowledge and support logs
- `Autograph` can become a secondary memory graph for research and relationship context
- support answers should still query `kb_api` first, even if graph memory exists

## Candidate Knowledge Workflow

### Goal

Allow the system to learn from solved support cases without silently polluting the approved KB.

### Rules

- solved support cases must not go directly into approved KB
- candidate knowledge should be created as a draft, not as canonical knowledge
- owner review must stay simple and visible inside Telegram
- no silent background accumulation of approved answers without owner awareness

### Recommended v1 Flow

1. a support case is solved or the agent detects a repeated KB gap
2. the system creates a `proposed_update`-style candidate knowledge draft
3. the owner receives a Telegram notification in operator flow with:
   - short title
   - why it was suggested
   - draft answer
4. the owner replies in natural language:
   - `подтверждаю`
   - `не добавляй`
   - `исправь так: ...`
5. only after owner approval does the item become approved KB

### UX Principle

The owner should not need slash commands for routine review. Natural-language approvals by reply are the preferred interface. Slash commands may remain only as a fallback.

### Anti-Goals

- no auto-approval into canonical KB
- no invisible backlog growing in the database without notifying the owner
- no repeated spam for the same unresolved candidate if deduplication can prevent it

## Next Implementation Block

The next implementation block after the current support listener is:

1. owner/operator flow with human-like responses
2. candidate knowledge notifications to the owner in Telegram
3. natural-language approve / reject / edit handling by reply
4. deduplication so repeated support gaps do not create noisy duplicate review items

## Recommended Tool Groups

### Support Tools

- `telegram_get_me`
- `telegram_resolve_peer`
- `telegram_get_messages`
- `telegram_send_message`
- `telegram_reply`
- `telegram_mark_read`

### Parsing Tools

- `telegram_list_dialogs`
- `telegram_get_channel_posts`
- `telegram_search_messages`
- `telegram_get_dialog_metadata`

Optional later:

- `telegram_download_media`
- `telegram_get_channel_participants`

### Publishing Tools

- `telegram_publish_message`
- `telegram_publish_media_post`

Optional later:

- `telegram_schedule_post`

## Recommendation Per Capability

### Support

Yes, automate this.

This is a strong fit for agent orchestration plus KB retrieval plus audit logging.

### Parsing

Yes, automate this, but as a separate tool group.

This is a strong fit for an agent because the workflow is repetitive and research-heavy.

### Publishing

Start with semi-manual publishing, not full autonomy.

Recommended v1:

- agent drafts post
- human reviews
- agent publishes only after explicit approval

Do not start with autonomous channel publishing.

## Recommended V1 Scope

### Included In V1

- `kb_api` bridge through OpenCrabs tools
- Telethon session bootstrap
- support message read/send/reply primitives
- support logging through `kb_api`
- channel parsing for dialogs, posts, and message search
- approval-gated publishing draft flow
- agent identity document drafted and stored in repo

### Not Included In V1

- autonomous public posting
- direct Telegram integration inside OpenCrabs runtime
- MCP-first Telegram integration
- broad raw Telethon access from OpenCrabs
- full outreach automation without review

## Why Publishing Should Be More Conservative

- brand tone risk
- accidental posting risk
- media attachment mistakes
- factual error amplification

If text and image are already prepared, manual posting may remain cheaper than full automation unless publishing volume is high.

## Good Uses For This Agent

- answer routine subscriber support questions
- log support conversations into `kb_api`
- detect KB gaps and create `proposed_updates`
- parse niche Telegram channels for partnership leads
- summarize channel activity for outreach decisions
- draft outreach messages for human approval
- draft public posts for FitMentor channels

## Uses To Avoid In V1

- fully autonomous public posting
- uncontrolled mass outreach
- direct Telegram session access from OpenCrabs
- mixing support and partnership actions into one undifferentiated tool surface

## Recommended Implementation Shape

### Telegram Runtime

Implement a separate real-user Telegram adapter with `Telethon`.

### OpenCrabs Integration

First use a narrow CLI bridge, not a full MCP server.

Reason:

- simpler runtime
- easier debugging
- lower integration risk
- already consistent with the `kb_api` bridge pattern

### Future Upgrade Path

If the adapter becomes stable and broad enough, wrap the same capabilities behind MCP later.

## Bridge Strategy

### Current Bridge Already In Place

`kb_api` is already integrated through a narrow CLI bridge pattern.

This is the pattern to reuse for Telegram:

- JSON input via stdin
- JSON output via stdout
- narrow command names
- no raw client exposure

### Planned Telegram Bridge

Recommended initial bridge path:

- `/opt/agent/workspace/fitmentor-agent/scripts/opencrabs_telegram_bridge.py`

It should expose separate commands for:

- support
- parsing
- publishing

while still sharing one Telethon runtime/session.

## Runtime Artifacts

Expected host-side structure:

- Telethon adapter runtime under `fitmentor-agent`
- CLI bridge script for OpenCrabs under `fitmentor-agent/scripts/`
- OpenCrabs tools config under `opencrabs-home/.opencrabs/tools.toml`

## Implementation Phases

### Phase 1. Stabilize Existing KB Integration

- keep `kb_api` bridge working
- keep OpenCrabs tools pointed at host paths
- verify support logging path
- keep this documented in the runbook

### Phase 2. Telethon Session Bootstrap

- add `api_id`
- add `api_hash`
- implement first interactive login
- persist session file safely
- document exact session file location
- initial implementation paths:
  - `services/telegram_adapter/app/login.py`
  - `scripts/opencrabs_telegram_bridge.py`

### Phase 3. Support Tooling

- implement read/send/reply/read-state commands
- connect support flow to `kb_api`
- log messages and thread ids
- define escalation path for uncertain support answers
- first V1 bridge commands:
  - `telegram_get_me`
  - `telegram_resolve_peer`
  - `telegram_get_messages`
  - `telegram_send_message`
  - `telegram_reply`
  - `telegram_mark_read`
  - `telegram_get_channel_posts`

### Phase 4. Parsing Tooling

- implement dialog/channel listing
- implement post retrieval
- implement basic search and metadata extraction
- shape outputs for partnership research workflows

### Phase 5. Publishing Tooling

- implement publish commands
- keep explicit approval barrier
- start with human-approved posting only

### Phase 6. OpenCrabs Orchestration

- add shell tools to `tools.toml`
- verify support workflow
- verify parsing workflow
- verify approval before publishing

## Immediate Next Steps

1. Keep `kb_api` bridge stable and documented.
2. Start the Telethon adapter as a separate implementation track.
3. Define the exact V1 Telegram command schema before coding.
4. Implement support commands first.
5. Implement parsing commands second.
6. Leave publishing approval-gated from day one.
7. Implement the first support orchestration loop on top of the existing bridges.
8. Evaluate `Autograph` only as a secondary long-term memory layer, not as a replacement for `kb_api`.

## Product Decision Guidance

### Should the agent be added to the FitMentor Telegram channel?

Yes, but not as a fully autonomous publisher in v1.

Best first use:

- drafting post copy
- drafting caption plus CTA
- optionally preparing publication payload

Final post action should stay human-approved first.

### Is automated publishing worth it?

Only if:

- post frequency is high
- content format is repeatable
- you already trust the drafting workflow

If posts are infrequent and already prepared with text plus image, manual publication is simpler in v1.

## Final Recommendation

Build one Telegram system with three scoped modes:

- support mode
- parsing mode
- publish mode

But expose them to OpenCrabs as separate tool groups with separate approval expectations.

That keeps the architecture clean and makes it possible to automate the useful parts without over-automating risky parts.
