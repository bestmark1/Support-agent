# OpenCrabs Integration

## Role Of OpenCrabs

OpenCrabs is the top-level agent runtime.

In this project it should not replace the application services. Instead, it should sit above them and use them as controlled capabilities.

## Recommended Split

### OpenCrabs

- orchestration layer
- reasoning layer
- tool-calling layer
- review and approval layer

### FitMentor Services

- `kb_api`: approved knowledge retrieval and `proposed_updates`
- `support_agent`: Telegram support flow
- `partnership_research`: partnership lead workflow

## Why This Split

- business logic stays in your own codebase
- data access stays narrow and auditable
- OpenCrabs does not need direct unrestricted DB access
- you can swap the agent layer later without rewriting the product services

## How OpenCrabs Should Use The System

OpenCrabs should call narrow tools such as:

- `search_knowledge(query, limit)`
- `create_proposed_update(...)`
- `list_partnership_leads(...)`
- `score_partnership_lead(...)`

Avoid giving OpenCrabs direct SQL or broad file access to the whole system.

## Security Model

- keep `approval_policy = "ask"`
- keep tools narrow
- keep support and partnership actions separated
- keep write access to approved knowledge out of the agent
