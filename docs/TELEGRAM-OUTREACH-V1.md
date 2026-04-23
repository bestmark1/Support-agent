# Telegram Outreach V1

## Goal

Find Telegram channels and chats relevant for FitMentor outreach, score them, and build a shortlist for manual review.

This is a discovery and scoring workflow, not an auto-outreach workflow.

## Search Queries

Use Telegram search with:

- `питание`
- `похудение`
- `ПП`
- `калории`
- `ЗОЖ`

## Target Types

- PP / healthy nutrition channels
- weight-loss channels and chats
- wellness / healthy lifestyle channels
- small fitness trainers
- nutritionists
- chats and marathons around fat loss / diet tracking

## Priority

Prefer channels and chats up to `5k–10k` subscribers or members.

Why:

- easier to start with barter
- less likely to demand cash immediately
- often more responsive
- easier to test conversion

Channels above `50k` should be treated as later-stage outreach.

## Partnership Model

Start with:

1. barter: free Premium access for `3–6` months
2. affiliate / partner code
3. free test first: try the bot, then tell the audience if it is useful

## Main CTA

Primary CTA should go directly to the bot:

- `https://t.me/fit_mentor_ai_bot`

The support surface is not the main CTA.

## Scoring V1

The first scoring pass uses:

- niche relevance
- audience size
- recent activity
- visible contact / advertising / collaboration signals

The score is heuristic and should be reviewed by hand.

## Script

Run:

```bash
cd /opt/agent/workspace/fitmentor-agent
source .venv/bin/activate
env PYTHONPATH=/opt/agent/workspace/fitmentor-agent python /opt/agent/workspace/fitmentor-agent/scripts/telegram_outreach_search.py
```

Optional:

```bash
env PYTHONPATH=/opt/agent/workspace/fitmentor-agent python /opt/agent/workspace/fitmentor-agent/scripts/telegram_outreach_search.py --queries питание похудение ПП --limit-per-query 15 --post-limit 6
```

## Output

The script returns JSON with:

- matched queries
- entity type
- title
- username / link
- audience size when available
- recent post samples
- heuristic score
- niche
- recommendation

## What To Do Next

1. run the script
2. inspect the shortlist
3. manually review the top leads
4. draft outreach only after shortlist review
