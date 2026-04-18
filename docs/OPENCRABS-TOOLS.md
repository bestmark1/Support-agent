# OpenCrabs Tool Surface

`OpenCrabs` should use the backend through narrow calls only.

## Current HTTP Surface

- `GET /kb/health`
- `GET /kb/search?query=...&limit=...`
- `POST /kb/proposed-updates`
- `POST /kb/support-threads`
- `POST /kb/support-messages`

## Purpose

- `search`: retrieve approved knowledge for semantic support answers
- `proposed-updates`: store unknown or weakly answered cases for human review
- `support-threads`: ensure thread identity for a support conversation
- `support-messages`: store user and assistant message logs

## Design Rule

Do not give `OpenCrabs` direct SQL access or broad file access when a narrow backend call is enough.
