# Task: Owner routing fix and reusable base outline

## Problem

- Owner messages could fall into `operator_mode` too aggressively because operator premium intent matched bare `premium` / `премиум`.
- There was no written extraction target for a reusable upgraded OpenCrabs base.

## Scope

- Narrow operator premium intent matching.
- Let owner messages with clear payment/access/support semantics go through support flow.
- Write a reusable base extraction outline.

## Acceptance checks

- Premium entitlement user text is not treated as operator summary intent.
- Owner support-like message can be routed as support flow without `/support_test`.
- Extraction target is documented.
