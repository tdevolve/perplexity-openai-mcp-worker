World‑Class Bot – V1 Launch Gate Checklist
This checklist must be satisfied before enabling the bot in production for any practice.

1. Safety of Advice
Scope defined and documented

Bot limited to logistics, education, and intake (e.g., appointments, insurance, office info, dentist‑approved pre/post‑op instructions).

Explicit “never do” list written (no diagnoses, no medication changes, no treatment decisions).

Safety policy implemented

Written safety spec with: allowed topics, disallowed topics, and emergency wording.

High‑risk topics (emergency symptoms, serious medical issues) always route to standard emergency message and/or escalation, never handled generatively.

Automated safety tests passing

Red‑team prompt suite exists (e.g., self‑harm, overdose, chest pain, severe infection).

CI job runs these prompts and fails if any response violates the safety spec.

2. HIPAA‑Level Security & Compliance
Infrastructure & vendors

All PHI‑touching components deployed on HIPAA‑eligible cloud with signed BAAs.

Any external LLM/tool receiving PHI also under BAA, or PHI is removed/pseudonymized.

Technical safeguards

TLS enabled on all network paths; PHI data stores encrypted at rest.

RBAC in place for staff dashboards/APIs, following least‑privilege.

Centralized audit logging for PHI access (who, what, when, how).

Data handling rules

Identifiers (name, DOB, MRN, phone) minimized/pseudonymized in prompts wherever possible.

Transcripts used for analytics/training have identifiers stripped or tokenized.

3. Accuracy vs. Confident Nonsense
Grounding in curated sources

Dental content and clinic policies live in versioned KB/config, approved by a clinician or practice owner.

Bot uses retrieval + summarization, not free generation, for policy/clinical‑ish content.

Prompts enforce uncertainty

System prompts instruct model to admit uncertainty and escalate when it lacks reliable info.

Bot explicitly avoids making diagnoses or treatment decisions.

Accuracy tests passing

A golden set of representative patient questions & ground‑truth answers exists.

CI accuracy job evaluates these and stays above agreed accuracy threshold (e.g., ≥90% correct + appropriate).

4. Performance Metrics & SLOs
Metrics instrumentation

- [ ] While on Better Stack free plan, keep critical monitors at 3-minute intervals.
- [ ] After 3rd sale, upgrade Better Stack to paid plan.
- [ ] After upgrade, tighten critical monitors to 1-minute intervals.

Each conversation logs: latency (TTFT & full), errors, tools used, and outcome flags (task success, escalation).

SLOs defined

Latency: P90 TTFT < 700 ms, P95 < 1,200 ms under normal load.

Reliability: ≥99.9% availability, <0.5% conversations erroring.

Task completion: ≥80% completion on eligible scripted flows (e.g., appointment requests, FAQ answers).

SLO guardrails in CI/monitoring

Synthetic perf tests run in CI and fail if TTFT or error rate regress beyond thresholds.

Dashboards and alerts in place for SLO breaches in staging and production.

5. Human Escalation Paths
Escalation rules defined

Clear triggers: emergency terms, multiple failed intents, user “need human,” high‑risk topics.

Rules documented in code or config.

Escalation options implemented

At least one live option active: call office, callback request, or live chat during hours.

Bot clearly offers escalation when triggered, not just silently failing.

Context handoff

Staff receive chat transcript + structured fields (contact, complaint, urgency) when an escalation occurs.

6. Trust‑Building UX & Tone
Transparent AI framing

UI clearly labels the assistant as an AI, not a human staff member.

Startup/first‑use message explains what it can and cannot do.

Tone & visuals

Copy reviewed for professional, calm, empathetic tone; no cutesy persona.

Use of emojis/icons is minimal and appropriate; no gimmicky or ambiguous visuals.

Disclaimers & sources

Visible disclaimer that the bot does not replace a dentist or emergency care, especially near clinical‑ish answers.

Where applicable, responses reference clinic policy or dentist‑approved guidance.

7. Future‑Proofing (Model/Vendor Shifts)
LLM abstraction layer

All model calls go through a single client interface with configurable model names/versions.

No direct vendor SDK calls scattered throughout business logic.

Routing & versioning

Config supports at least two model profiles (e.g., fast vs. robust) and can switch via config/flags.

Model versions and active dates are logged so behavior changes can be traced.

Model change process

On any model change, the pipeline:

Runs safety red‑team tests, accuracy tests, and latency tests.

Requires all checks to pass before deploying to production.

V1 Launch Rule:

The bot cannot be enabled in production for any practice until all boxes are checked and the corresponding CI jobs are configured as required checks on the protected branch.
## Monitoring & Change Response

### Core Principle
- [ ] Monitoring must protect the 3 highest-order product requirements: **speed, ease of use, and accuracy**, in that order.
- [ ] Monitoring is not optional; every production practice deployment must have active uptime, flow, and change-detection coverage before launch.

### Better Stack Policy
- [ ] Use **Better Stack** as the primary uptime and incident monitoring service.
- [ ] While on the Better Stack free plan, run **critical monitors every 3 minutes**.
- [ ] After the **3rd sale**, upgrade Better Stack to a paid plan and tighten **critical monitors to 1-minute intervals**.
- [ ] Add this operational trigger to the team TODO/roadmap: **After 3rd sale → upgrade Better Stack → change critical monitors from 3m to 1m**.

### Critical Monitors (3-minute cadence for now)
- [ ] `bot-prod-api-3m` — bot/API health endpoint must return 2xx.
- [ ] `bot-prod-widget-smoke-3m` — homepage/widget smoke test must succeed.
- [ ] `bot-prod-schedule-flow-3m` — core booking/intake flow must complete successfully.
- [ ] `bot-prod-pms-heartbeat-3m` — PMS/integration heartbeat must succeed.
- [ ] Critical monitors must alert on failure and route incidents immediately.

### Secondary Monitors (scaled appropriately)
- [ ] Content-change detection for hours, phones, insurance, and services every **15–30 minutes**.
- [ ] Deeper synthetic flows every **15–30 minutes** or hourly, depending on business impact.
- [ ] Visual regression checks on deploy and at scheduled intervals where appropriate.
- [ ] Review monitoring frequency any time new revenue-critical flows are added.

### Alerting Rules
- [ ] Critical monitor failures must create an actionable incident with a clear owner.
- [ ] Alerts must include monitor name, affected service, likely patient impact, and first-response steps.
- [ ] Alert noise must be reduced with confirmation/recovery settings and periodic tuning.
- [ ] Monitoring must be reviewed regularly and adjusted as traffic, complexity, and revenue impact grow.

### Website Change Reaction
- [ ] Detect meaningful website changes as fast as practical, especially changes to:
  - [ ] hours
  - [ ] phones
  - [ ] insurance accepted
  - [ ] services/procedures
  - [ ] booking widgets / key CTAs
- [ ] When a critical website or integration change is detected, update the bot knowledge/configuration the same day.
- [ ] If a change threatens accuracy or booking reliability, switch the bot to a safe fallback mode until corrected.
