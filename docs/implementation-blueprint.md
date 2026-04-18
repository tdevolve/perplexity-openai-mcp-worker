# Implementation Blueprint
## Multi-Tenant AI Service Platform

## Purpose

This blueprint translates the platform architecture into a repo-facing implementation plan.

The objective is to build a shared, modular, multi-tenant AI service platform that supports:
- conversational interfaces
- customer lifecycle workflows
- retrieval and knowledge grounding
- external integrations
- governance and analytics
- MCP as one adapter layer

The system should be structured so that each module can stand alone, but still work in harmony through shared contracts, tenant-aware orchestration, and a common platform core.

---

## Repo Strategy

Use a **modular monolith first**.

That means:
- one deployable backend service
- clear internal module boundaries
- shared auth, config, logging, and tenant resolution
- the option to split modules into separate services later only if scale or operational needs justify it

This keeps the system fast to build and maintain early, while preserving clean architecture for future extraction.

---

## Recommended Repo Name

Use a broader platform name rather than a vertical-specific bot name.

Suggested examples:
- `ai-service-platform`
- `multi-tenant-ai-platform`
- `bot-platform-core`
- `commercial-ai-platform`

---

## Recommended Project Structure

```text
ai-service-platform/
├── app/
│   ├── __init__.py
│   ├── factory.py
│   ├── config.py
│   ├── extensions.py
│   ├── middleware/
│   │   ├── request_id.py
│   │   ├── tenant_context.py
│   │   ├── auth.py
│   │   └── error_handlers.py
│   ├── routes/
│   │   ├── health.py
│   │   ├── chat.py
│   │   ├── lifecycle.py
│   │   ├── admin.py
│   │   ├── analytics.py
│   │   └── mcp.py
│   ├── services/
│   │   ├── orchestrator.py
│   │   ├── interaction_service.py
│   │   ├── lifecycle_service.py
│   │   ├── retrieval_service.py
│   │   ├── integration_service.py
│   │   ├── analytics_service.py
│   │   ├── governance_service.py
│   │   ├── tenant_service.py
│   │   └── llm_service.py
│   ├── repositories/
│   │   ├── tenant_repository.py
│   │   ├── conversation_repository.py
│   │   ├── event_repository.py
│   │   ├── document_repository.py
│   │   └── prompt_repository.py
│   ├── models/
│   │   ├── tenant.py
│   │   ├── conversation.py
│   │   ├── event.py
│   │   ├── prompt_version.py
│   │   └── audit_log.py
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── lifecycle.py
│   │   ├── tenant.py
│   │   └── admin.py
│   ├── tenants/
│   │   ├── default/
│   │   │   ├── tenant.json
│   │   │   ├── prompts.json
│   │   │   ├── policies.json
│   │   │   └── knowledge/
│   │   └── sample-tenant/
│   │       ├── tenant.json
│   │       ├── prompts.json
│   │       ├── policies.json
│   │       └── knowledge/
│   ├── adapters/
│   │   ├── mcp/
│   │   │   ├── server.py
│   │   │   ├── tools.py
│   │   │   ├── resources.py
│   │   │   └── transport.py
│   │   ├── crm/
│   │   ├── scheduling/
│   │   ├── messaging/
│   │   └── documents/
│   └── utils/
│       ├── logging.py
│       ├── ids.py
│       ├── time.py
│       └── json.py
├── tests/
│   ├── test_health.py
│   ├── test_chat.py
│   ├── test_tenant_resolution.py
│   ├── test_lifecycle.py
│   └── test_mcp.py
├── migrations/
├── docs/
│   ├── architecture-sheet.md
│   ├── api-contracts.md
│   ├── tenant-schema.md
│   └── roadmap.md
├── scripts/
│   ├── seed_tenant.py
│   ├── import_knowledge.py
│   └── backfill_events.py
├── requirements.txt
├── .env.example
├── run.py
├── gunicorn.conf.py
├── Procfile
└── README.md
```

---

## Module-to-Platform Mapping

| Platform capability | Implementation module |
|---|---|
| AI interaction layer | `routes/chat.py`, `services/interaction_service.py`, `services/orchestrator.py` |
| Customer lifecycle layer | `routes/lifecycle.py`, `services/lifecycle_service.py` |
| Retrieval layer | `services/retrieval_service.py`, `repositories/document_repository.py`, `tenants/*/knowledge/` |
| Integration layer | `adapters/crm/`, `adapters/scheduling/`, `adapters/messaging/`, `adapters/documents/` |
| Admin & governance layer | `routes/admin.py`, `services/governance_service.py`, `models/audit_log.py` |
| Analytics layer | `routes/analytics.py`, `services/analytics_service.py`, `models/event.py` |
| MCP adapter layer | `routes/mcp.py`, `adapters/mcp/` |

---

## Core Architectural Rules

### 1. Tenant context is mandatory
Every request must resolve a tenant before business logic runs.

Allowed sources:
- request header
- subdomain
- signed token
- explicit tenant ID in trusted internal calls

No service should run tenant-blind.

### 2. Authentication is global, authorization is tenant-scoped
User identity can exist globally, but permissions, policies, and access checks must be evaluated in tenant context.

### 3. Modules may depend only on contracts, not internals
A module can call another module through a service interface, repository contract, or event boundary, but should not directly reach into another module’s internal implementation.

### 4. MCP is an adapter, not the core
MCP should expose selected capabilities already implemented in the platform. It should not become the place where core lifecycle, retrieval, or tenant logic lives.

### 5. Start with file-backed tenant config, then move to Postgres
Early on, `tenant.json` and local knowledge packs are fine. Production should move to Postgres-backed tenant records, prompt versions, audit logs, and analytics events.

---

## Initial Endpoints

### Platform health
- `GET /`
- `GET /health`
- `GET /ready`

### Interaction
- `POST /chat`
- `POST /chat/stream` later if needed

### Lifecycle
- `POST /lifecycle/intake`
- `POST /lifecycle/advance`
- `POST /lifecycle/repeat-service`

### Admin
- `GET /admin/tenants/:tenant_id`
- `POST /admin/tenants/:tenant_id/test-chat`
- `GET /admin/tenants/:tenant_id/events`

### Analytics
- `POST /events`
- `GET /analytics/summary`

### MCP
- `POST /mcp`
- or transport-specific MCP routes as needed by implementation

---

## Minimum Request Contracts

### `POST /chat`
```json
{
  "tenant_id": "sample-tenant",
  "session_id": "sess_123",
  "user_id": "user_abc",
  "message": "I need help with a repeat appointment",
  "context": {
    "channel": "website",
    "locale": "en-US"
  }
}
```

### `POST /lifecycle/intake`
```json
{
  "tenant_id": "sample-tenant",
  "session_id": "sess_123",
  "lead": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "555-555-5555"
  },
  "intent": "new-service-request"
}
```

### `POST /events`
```json
{
  "tenant_id": "sample-tenant",
  "session_id": "sess_123",
  "event_type": "chat_response_rendered",
  "metadata": {
    "channel": "website"
  }
}
```

---

## Tenant Configuration Schema

Create one `tenant.json` per tenant.

Example:

```json
{
  "tenant_id": "sample-tenant",
  "name": "Sample Tenant",
  "domain": "example.com",
  "industry": "commercial-services",
  "status": "active",
  "branding": {
    "primary_color": "#01696f",
    "logo_url": "",
    "display_name": "Sample Tenant"
  },
  "voice": {
    "tone": "clear, calm, professional",
    "reading_level": "plain-language",
    "allow_humor": false
  },
  "languages": ["en", "es"],
  "channels": ["website", "admin", "mcp"],
  "features": {
    "chat": true,
    "retrieval": true,
    "lead_capture": true,
    "repeat_service_flows": true,
    "analytics": true,
    "mcp": true
  },
  "models": {
    "chat_model": "gpt-4.1",
    "fallback_model": "gpt-4.1-mini"
  },
  "policies": {
    "store_conversations": true,
    "redact_sensitive_fields": true,
    "allow_file_search": true,
    "require_handoff_on_risk": true
  },
  "integrations": {
    "crm": {
      "enabled": false,
      "provider": null
    },
    "scheduling": {
      "enabled": false,
      "provider": null
    },
    "messaging": {
      "enabled": false,
      "provider": null
    }
  }
}
```

---

## Prompt and Policy Files

### `prompts.json`
Holds tenant-specific prompts by use case:
- greeting
- system behavior
- escalation behavior
- translation behavior
- repeat-service flow
- intake flow

### `policies.json`
Holds rules for:
- sensitive topics
- escalation requirements
- allowed sources
- retention windows
- compliance toggles
- messaging constraints

---

## Data Model Priorities

Move toward Postgres tables for:

- `tenants`
- `tenant_domains`
- `users`
- `tenant_memberships`
- `conversations`
- `conversation_messages`
- `lifecycle_records`
- `events`
- `prompt_versions`
- `audit_logs`

Keep tenant-scoped foreign keys explicit.

---

## Recommended App Factory Pattern

Use Flask app factory + blueprints.

Example shape:

- `app/factory.py` creates app
- registers config
- registers middleware
- registers blueprints from `app/routes`
- initializes extensions
- attaches error handlers

This keeps `run.py` thin and avoids a single growing `main.py`.

---

## How Existing Repos Map Forward

### `perplexity-openai-mcp-worker`
Current role:
- seed for the interaction layer
- health endpoints
- base request handling
- MCP-adjacent adapter experimentation

Recommended evolution:
- move from single-file `main.py` into app factory + blueprints
- rename `/ask_openai` to broader platform-facing route names like `/chat`
- keep MCP-specific logic isolated in `adapters/mcp/`

### `dental-bot-template`
Current role:
- seed for tenant-specific deployment patterns
- source for retrieval, worker patterns, and domain-grounded bot behavior

Recommended evolution:
- stop treating it as the permanent architectural center
- extract reusable modules into the shared platform
- treat dental as one tenant pattern, not the platform identity

---

## Phase 1 Build Checklist

### Phase 1A — foundation
- [ ] create app factory structure
- [ ] add health, ready, and chat blueprints
- [ ] add request ID and tenant context middleware
- [ ] define request/response schemas
- [ ] add structured logging

### Phase 1B — tenant model
- [ ] create `app/tenants/default/tenant.json`
- [ ] implement tenant resolution from header
- [ ] load prompts and policies by tenant
- [ ] block requests with missing or invalid tenant context

### Phase 1C — orchestration and retrieval
- [ ] create `orchestrator.py`
- [ ] create `interaction_service.py`
- [ ] create `retrieval_service.py`
- [ ] support tenant knowledge loading from local files
- [ ] return grounded responses with source references where applicable

### Phase 1D — lifecycle
- [ ] add intake endpoint
- [ ] add lifecycle record model
- [ ] support lead capture and repeat-service state
- [ ] emit lifecycle events to analytics

### Phase 1E — admin and analytics
- [ ] add event ingestion endpoint
- [ ] add tenant test endpoint
- [ ] add audit logging
- [ ] add simple analytics summary view

### Phase 1F — MCP adapter
- [ ] isolate MCP transport and tools in `adapters/mcp/`
- [ ] expose only stable platform capabilities
- [ ] ensure MCP calls reuse core services instead of duplicating logic

---

## Phase 1 Definition of Done

Phase 1 is done when:
- one shared Flask app serves multiple tenants
- `/chat` works with tenant-scoped prompts and knowledge
- tenant context is required and enforced
- lifecycle intake and repeat-service state exist
- events and audit logs are captured
- MCP can call stable platform capabilities through an adapter layer
- no module depends on another module’s internals

---

## First Practical Refactor

If starting from the current worker repo, do this first:

1. create `app/`
2. move `main.py` logic into `app/factory.py`
3. split `/health` and `/ask_openai` into `routes/health.py` and `routes/chat.py`
4. rename `/ask_openai` to `/chat`
5. add `middleware/tenant_context.py`
6. create `tenants/default/tenant.json`
7. add `services/orchestrator.py`