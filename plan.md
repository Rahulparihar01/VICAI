# Phase 0 (P0) Analysis and Implementation Plan

This document outlines the current state of the codebase against the **VicAI Phase 0 (P0) - Investor / Lighthouse Release** requirements, identifies what is missing, and provides a structured workflow for completing the P0 build.

## User Review Required

Please review the proposed development flow below. Since P0 is budget-gated (A$30,000), we must ensure we strictly stick to the P0 items and do not bleed into P1/P2.

## Open Questions

As per Section 19 of the MVP brief, several decisions affect the exact P0 scope. Please clarify the following before we begin the next sprints:
1. **Plan Entitlements**: What are the exact entitlements (usage/users/locations/agents/integrations) per tier (Starter / Growth / Pro)?
2. **Email Provider**: Which email provider is strictly P0: Microsoft 365, Gmail, or both?
3. **Billing**: Is the Xero API mandatory for release 1, or is CSV export acceptable?
4. **Pause Services**: Can customers self-pause services, or only VicAI internal admins?
5. **Call Recording**: What is the default for call recording: on, opt-in, or off for the lighthouse client?
6. **Overage Pricing**: What is the overage pricing model: pass-through, markup, or bundled?

---

## Codebase Analysis: What's Complete vs. Pending

### 1. Foundation & Auth (Mostly Complete ✅)
- **Complete**: 
  - FastAPI structure, SQLAlchemy DB setup (`database.py`, `models.py`).
  - `Tenant` and `User` models for multi-tenant identity.
  - Basic RBAC foundation (`super_admin`, `internal_admin`, `customer` roles).
  - JWT Authentication (`auth.py`).
  - Internal Admin endpoints (`internal_admin.py`) for managing users and organizations.
- **Pending (P0)**: 
  - Front-end portals (Custom branded customer & internal admin portals).
  - Shared design system.

### 2. Commercial Onboarding (Pending ❌)
- **Complete**: Tenant and User registration logic (`auth.py`).
- **Pending (P0)**:
  - Plan selection (Starter / Growth / Pro).
  - Stripe payment method setup (hosted/embedded).
  - Onboarding checklist and state model (Created → Payment pending → Configuring → Ready for testing → Active).

### 3. Channels & Unified Inbox (Pending ❌)
- **Complete**: None yet.
- **Pending (P0)**:
  - **Channels**: Voice (Telnyx + Retell), SMS (ClickSend), Website chat widget, One Email provider.
  - **Inbox**: Channel/status filters, ticket assignment, internal notes, tags.
  - **Contacts**: Contact timeline, transcripts, delivery status.
  - **Replies**: Human replies with visible AI/human authorship.

### 4. AI Agents (Pending ❌)
- **Complete**: None yet.
- **Pending (P0)**:
  - Agent configuration (identity, brand/tone, knowledge, goals).
  - Draft mode and controlled auto-send mode.
  - Basic testing simulator (scenario/test chat/test call).

### 5. Dashboards, Usage, and Admin Health (Pending ❌)
- **Complete**: None yet.
- **Pending (P0)**:
  - Raw usage event capture (append-only, idempotent, tenant-attributed).
  - Core/executive-level dashboard for customers.
  - Internal tenant health view (for admins).
  - Service pause/resume controls with audit trails.

### 6. Reputation & Billing (Pending ❌)
- **Complete**: None yet.
- **Pending (P0)**:
  - Google Business Profile review dashboard + AI reply workflow.
  - Manual/import fallback for reviews.
  - Stripe subscription state mapped to tenant lifecycle.
  - CSV usage/invoice export.

---

## Proper Flow for Completing P0

Following the suggested sequencing from the MVP brief, here is the step-by-step technical implementation flow for the pending work:

### Phase A: Commercial Onboarding & Stripe
- **Models/DB**: Add `Plan` and `Subscription` tables linked to `Tenant`. Add `onboarding_state` to `Tenant`.
- **Integrations**: Integrate Stripe API for creating Checkout Sessions and handling webhooks (payment success/failure).
- **API**: Build endpoints for plan selection, Stripe checkout URL generation, and onboarding state updates.

### Phase B: Core Channels (Voice, SMS, Chat, Email)
- **Models/DB**: Add `Channel`, `Contact`, `Message`, and `Thread` tables.
- **Integrations**:
  - ClickSend API for SMS sending and webhook receiving.
  - Telnyx + Retell API for Voice AI integration.
  - Setup webhook endpoints in FastAPI for receiving inbound messages.
- **API**: Unified inbox endpoints (list threads, fetch messages, add internal notes, assign threads).

### Phase C: AI Agents & Knowledge
- **Models/DB**: Add `Agent`, `AgentKnowledge`, and `AgentPolicy` tables.
- **API**: Endpoints to configure AI Agent identity and tone.
- **Logic**: Implement the "Draft vs. Auto-send" control logic in the inbound message webhook handlers. Route inbound messages to the LLM backend if auto-send is enabled.

### Phase D: Dashboards & Usage Metering
- **Models/DB**: Add an append-only `UsageEvent` table (tenant_id, event_type, amount, timestamp, idempotent_key).
- **Logic**: Instrument all channel sends and AI invocations to log usage events.
- **API**: Aggregation endpoints for the customer core dashboard and internal admin health view.
- **Controls**: Endpoints for internal admins (or customers, pending answer to Open Q #4) to pause/resume tenant services.

### Phase E: Reputation & Billing Export
- **Integrations**: Integrate Google Business Profile API for fetching reviews.
- **Models/DB**: Add `Review` table.
- **API**: Endpoints for displaying reviews and drafting AI replies.
- **Billing**: Endpoint to aggregate `UsageEvent` data for a billing period and generate a CSV export for Xero/manual invoicing.

## Verification Plan

### Automated Tests
- Write `pytest` integration tests for the Stripe webhook handlers to ensure tenant state changes correctly.
- Test the Unified Inbox endpoints and RBAC rules (ensure tenants cannot see other tenants' messages).
- Test usage metering idempotency (ensure duplicate webhooks don't double-charge).

### Manual Verification
- Go through the full self-onboarding path (UI → Stripe → Configuration).
- Send a test SMS to the system and verify it appears in the Unified Inbox.
- Generate a billing CSV and verify the math against known test usage events.
