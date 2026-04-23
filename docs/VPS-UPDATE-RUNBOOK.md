# VPS Update Runbook

Short path for updating the FitMentor agent on the VPS without recreating drift.

## Goal

Keep GitHub as the source of truth and keep local runtime state narrow.

Persist locally on the VPS only:

- `.env`
- `.secrets/`
- `.venv/`

Everything else should come from the repository.

## Standard Update Path

From the VPS:

```bash
cd /opt/agent/workspace/fitmentor-agent
git fetch origin
git checkout main
git pull --ff-only origin main
```

Then restart the listener:

```bash
systemctl restart fitmentor-telegram-listener
```

## Verification

After update:

```bash
cd /opt/agent/workspace/fitmentor-agent
git rev-parse HEAD
git status --short
git remote -v
systemctl status fitmentor-telegram-listener --no-pager -l
curl -s http://127.0.0.1:8010/kb/health
```

Expected:

- `git status --short` is empty
- `origin` does not contain embedded credentials
- listener is `active (running)`
- `kb_api` returns `{"status":"ok"}`

## If The Workspace Drifts Again

If the workspace becomes a mix of old tracked files and new untracked runtime files, do not force `git pull`.

Use the normalization approach instead:

1. stop the listener
2. move the old workspace aside as a backup
3. clone a fresh repo to the original path
4. restore `.env`, `.secrets`, `.venv`
5. restart the listener

## Runtime Notes

- `fitmentor-telegram-listener.service` runs from `/opt/agent/workspace/fitmentor-agent`
- the listener imports code directly from that workspace through `PYTHONPATH`
- changing tracked Python files in the workspace requires a listener restart to take effect
