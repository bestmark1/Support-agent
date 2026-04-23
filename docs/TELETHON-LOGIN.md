# Telethon Login

## Purpose

Bootstrap a real-user Telegram session for the FitMentor Telegram adapter.

## Required Environment

Set these values in the host-side `.env` used by `fitmentor-agent`:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- optional `TELEGRAM_PHONE`
- optional `TELEGRAM_SESSION_PATH`

Recommended session path on the VPS:

```text
/opt/agent/workspace/fitmentor-agent/.secrets/telethon_support.session
```

## First Login

From the repo root:

```bash
cd /opt/agent/workspace/fitmentor-agent
python3 -m services.telegram_adapter.app.login
```

The script will:

1. ask for phone number if `TELEGRAM_PHONE` is not set
2. send a Telegram login code
3. ask for the code
4. ask for 2FA password if needed
5. store the resulting session file

## After Login

Smoke test the bridge:

```bash
printf '%s\n' '{}' | python3 /opt/agent/workspace/fitmentor-agent/scripts/opencrabs_telegram_bridge.py telegram_get_me
```

Expected result:

```json
{"ok": true, "result": {...}}
```
