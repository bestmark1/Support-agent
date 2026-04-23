# Upgraded OpenCrabs Base

## Goal

Выделить из текущего FitMentor support-agent переиспользуемую базу, которую можно подключать в другой проект без FitMentor-специфики.

## Что должно остаться в базе

- Telegram transport через Telethon
- message loop и listener runtime
- operator mode
- owner review mode для candidate knowledge drafts
- support thread logging через HTTP API
- candidate KB proposal flow
- smoke tests для listener guard и reply routing
- простой deploy/runbook и Forkflow light

## Что должно быть вынесено из базы

- FitMentor-specific reply copy
- FitMentor-specific support intents
- FitMentor internal subscription/payment checks
- FitMentor KB schemas/content seeds
- FitMentor-specific docs и runbooks

## Рекомендуемая структура нового репозитория

```text
opencrabs-agent/
  packages/common/
    models/
    schemas/
    settings/
  services/kb_api/
    app/api/
    app/repositories/
    app/services/
  services/telegram_adapter/
    app/client.py
    app/commands.py
    app/config.py
    app/runtime.py
    app/operator_flow.py
    app/review_flow.py
    app/support_runtime.py
    app/transports/
  services/support_core/
    app/intents.py
    app/replies.py
    app/candidates.py
    app/threading.py
    app/hooks.py
  scripts/
    support_listener.py
  tests/
```

## Минимальные extension points

- `build_reply(context) -> ReplyDecision`
- `detect_issue_bucket(context) -> str`
- `fetch_account_context(user_id) -> dict | None`
- `should_create_candidate(context) -> bool`
- `build_candidate_draft(context) -> dict | None`

## Что я бы сделал в этом репо перед extraction

1. Разрезать `services/telegram_adapter/app/support_flow.py` на:
   - `operator_flow.py`
   - `review_flow.py`
   - `support_core/intents.py`
   - `support_core/replies.py`
   - `support_core/candidates.py`
   - `support_runtime.py`
2. Вынести FitMentor-specific functions за hooks:
   - `fitmentor_support_subscription_check`
   - FitMentor reply copy
   - FitMentor bucket naming
3. Оставить в базе только generic contracts и transport/runtime.

## Практический результат

После этого новый проект сможет:

- подменить только intents/replies/hooks;
- оставить тот же Telegram runtime;
- оставить тот же KB candidate/review path;
- не тащить FitMentor-specific слова, тарифы и внутренние проверки.
