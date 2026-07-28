# VicAI — Step-by-Step Frontend and Backend Implementation Guide

**Purpose:** Provide the exact build order for the VicAI MVP, starting with a working login page and backend authentication, then adding each product capability as a complete frontend/backend vertical slice.

**Related plan:** `VicAI_Phase_Wise_Implementation_Plan.md`

**Marketing homepage:** `index.html`

## 1. How to use this guide

Do not build all frontend screens first and connect the backend later. Complete one secure vertical slice at a time:

1. confirm the story and acceptance criteria;
2. design the database change;
3. write and apply the migration;
4. add row-level security and permission rules;
5. define the API/event contract;
6. implement the backend service;
7. build the frontend against the real contract;
8. add unit, integration, security, and end-to-end tests;
9. deploy to staging and demonstrate the outcome;
10. proceed only after the slice passes its exit gate.

The first product slice is **login plus backend authentication**. Organisation setup, dashboard, billing, inbox, and AI work begin only after authentication and tenant isolation are proven.

## 2. Recommended application architecture

Use the architecture named in the client brief:

- Next.js/React for the marketing site, customer portal, and internal admin portal
- Supabase Postgres, Auth, Storage, Realtime, and Edge Functions where appropriate
- A server-side VicAI API/integration layer for vendor access and policy enforcement
- Chatwoot behind the VicAI UI for approved inbox primitives
- Retell plus Telnyx for voice
- ClickSend for SMS
- OpenAI through a server-side VicAI model gateway
- Stripe for subscription/payment state
- n8n only for asynchronous workflows, never in the live-call synchronous path
- Sentry plus infrastructure monitoring

Pin approved stable dependency versions in the lockfile. Do not depend on floating package versions.

### 2.1 Suggested repository structure

```text
vicai/
├── apps/
│   ├── marketing/             # Public VicAI website
│   ├── customer-portal/       # Authenticated customer product
│   ├── admin-portal/          # Authenticated VicAI staff product
│   └── api/                   # Node API if functions alone are insufficient
├── packages/
│   ├── ui/                    # Shared VicAI design system
│   ├── auth/                  # Session, guards, membership and MFA helpers
│   ├── db/                    # Generated database types and repository layer
│   ├── contracts/             # Request, response and event schemas
│   ├── permissions/           # Capability catalogue and policy helpers
│   ├── integrations/          # Provider adapters and connector contracts
│   ├── observability/         # Logging, tracing and error helpers
│   └── config/                # Shared lint, TypeScript and environment rules
├── supabase/
│   ├── migrations/
│   ├── functions/
│   ├── seed.sql
│   └── tests/
├── tests/
│   ├── e2e/
│   ├── contract/
│   ├── security/
│   └── fixtures/
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── runbooks/
│   └── decisions/
└── .env.example
```

If a monorepo is considered too heavy for the first release, keep the same logical boundaries in one Next.js repository. Do not merge customer and internal permissions merely to simplify folder structure.

### 2.2 Application routes

#### Public marketing

```text
/
/privacy
/terms
/contact
```

#### Authentication

```text
/login
/forgot-password
/reset-password
/verify-email
/auth/callback
/mfa/setup
/mfa/verify
```

#### Customer portal

```text
/app
/app/onboarding
/app/inbox
/app/customers
/app/agents
/app/analytics
/app/reputation
/app/integrations
/app/usage-billing
/app/users
/app/settings
```

#### Internal admin portal

```text
/admin
/admin/tenants
/admin/tenants/:organisationId
/admin/usage
/admin/billing
/admin/incidents
/admin/integrations
/admin/audit
/admin/settings
```

### 2.3 Backend boundaries

- Browser code may use the public Supabase client only for permitted authentication/realtime operations.
- The browser must never receive service-role keys, OAuth client secrets, provider tokens, telephony credentials, OpenAI keys, Stripe secret keys, or integration API keys.
- Tenant identity must come from the verified session and membership, not a trusted browser-supplied `organisation_id`.
- Every write must pass authentication, capability permission, scope, validation, tenant ownership, and audit rules.
- Every provider webhook must pass signature validation, replay-window validation, idempotency, tenant/provider mapping, and safe error handling.
- Every billable provider event must create an append-only usage event.

## 3. Build-order summary

| Order | Vertical slice | Frontend result | Backend result |
|---:|---|---|---|
| 0 | Project foundation | Shared design tokens and application shells | Environments, CI/CD, migrations, logging, secrets |
| 1 | Login and authentication | Working login/recovery/verification screens | Secure session, Auth callback, guards, audit |
| 2 | Organisations and access | Organisation selection/setup and user access UI | Membership, RBAC, RLS, invitations, scopes |
| 3 | Customer app shell and home | Navigation and real basic dashboard | Tenant summary and readiness APIs |
| 4 | Commercial onboarding | Resumable onboarding and plan/payment screens | Lifecycle, entitlements, Stripe and webhooks |
| 5 | Integration centre foundation | Connector catalogue and health screens | OAuth/secret framework, tests, health, webhooks |
| 6 | Inbox and contacts core | Inbox, conversation, contact timeline | Normalised events, conversations, assignment |
| 7 | Website chat | Install/test widget and chat inbox | Widget sessions, allowed domains, webhooks |
| 8 | SMS | SMS conversation and delivery state | ClickSend send/receive, receipts, opt-out, usage |
| 9 | Voice | Calls, transcripts, outcomes and handover | Retell/Telnyx routing, transfer, call usage |
| 10 | Email | Mailbox connection and email conversations | One OAuth mailbox provider and message sync |
| 11 | AI agents and knowledge | Agent editor, testing, versions and modes | Retrieval, policy, tool gateway, model gateway |
| 12 | Customer analytics | KPI dashboard, freshness and exports | Event aggregation and scoped reporting |
| 13 | Reputation | Review queue, drafts, approvals and trends | Google reviews or fallback, tasks and publishing |
| 14 | Usage and billing | Plan, allowance, usage and invoice view | Ledger, reconciliation, snapshot and CSV |
| 15 | Internal admin portal | Tenant portfolio, health and diagnostics | Cross-tenant authorised views and incidents |
| 16 | Service controls and support | Pause/resume impact and support-access UI | State enforcement, support session and audit |
| 17 | Hardening and launch | Complete usable lighthouse experience | Security, recovery, monitoring and operations |
| 18 | P1 expansion | Additional product capabilities | ServiceM8, Xero, Meta, WhatsApp and second email |

## 4. Step 0 — project and environment foundation

### Goal

Create a repeatable development environment before implementing product screens.

### Frontend tasks

- Initialise the customer portal, admin portal, and marketing application.
- Add TypeScript strict mode.
- Create the shared colour, typography, spacing, radius, shadow, status, and responsive tokens.
- Create accessible primitives: button, input, select, textarea, modal, toast, table, tabs, badge, empty state, skeleton, error state, and confirmation dialog.
- Add customer and admin layout placeholders without business data.
- Add global error and not-found pages.

### Backend/platform tasks

- Create Supabase development and staging environments.
- Define the production environment creation process without using production secrets locally.
- Configure migrations, generated types, seed fixtures, and local reset.
- Add environment-variable validation at application startup.
- Configure CI for install, typecheck, lint, unit tests, build, migration checks, and security scanning.
- Configure staging deployments.
- Add structured JSON logs, request/trace IDs, Sentry, and redaction rules.
- Create a secrets register containing secret name, owner, environment, rotation process, and consuming service.

### Initial files

```text
.env.example
packages/config/env.ts
packages/observability/logger.ts
packages/contracts/errors.ts
packages/ui/tokens.css
supabase/migrations/0001_foundation.sql
docs/architecture/system-context.md
docs/decisions/ADR-001-application-boundaries.md
```

### Environment categories

```text
Public browser values:
- Application URL
- Public Supabase URL
- Supabase anonymous key

Server-only values:
- Supabase service role
- Stripe secret and webhook secret
- OpenAI key
- Retell key
- Telnyx key
- ClickSend credentials
- OAuth client secrets
- Encryption/secrets-management references
```

### Tests

- Application builds with an example environment file.
- Missing required variables fail with a safe message.
- Server-only variables cannot be imported into client bundles.
- Logs redact passwords, tokens, cookies, authorisation headers, card data, and integration secrets.
- A migration can run from an empty database and can be reproduced in CI.

### Exit gate

The three applications build in CI, staging is reachable, migrations are repeatable, and secrets are correctly separated.

## 5. Step 1 — login page with backend authentication

### Goal

Deliver the first complete product slice: a user can securely sign in, receive a server-validated session, and reach the correct protected application.

### 5.1 Frontend screens

Build these screens in order:

1. `/login`
2. `/forgot-password`
3. `/reset-password`
4. `/verify-email`
5. `/auth/callback`
6. `/mfa/verify` for internal administrators

### Login page requirements

- VicAI logo and consistent design system
- Email and password fields with real labels
- Show/hide password control
- Submit/loading/disabled states
- Generic invalid-credential message
- Link to password recovery
- Link back to the marketing homepage
- Keyboard navigation and visible focus
- Password-manager-compatible autocomplete attributes
- No indication that reveals whether a specific email exists
- No password or full authentication response written to logs

### 5.2 Backend authentication flow

```text
Login form
   ↓
VicAI server action or /api/auth/login
   ↓
Supabase Auth verifies credentials
   ↓
Secure HTTP-only session cookies are created/refreshed
   ↓
Server loads user profile and active memberships
   ↓
Internal user → /admin
One customer organisation → /app
Multiple organisations → organisation selector
No membership → controlled account-setup state
```

### Backend tasks

- Configure Supabase Auth email/password flow.
- Configure approved site URLs and redirect URLs by environment.
- Implement server-side session-cookie handling.
- Implement session refresh compatible with server-rendered routes.
- Add a protected-route middleware/guard.
- Add authentication rate limiting and abuse monitoring.
- Add secure logout that revokes/clears the current session.
- Add password-reset request and callback validation.
- Require verified email before customer onboarding.
- Require MFA for internal administrators.
- Write login success, logout, password-reset request, MFA and privileged authentication events to the audit stream without storing passwords or tokens.

### Initial tables

```text
profiles
- user_id uuid primary key references auth.users
- user_type enum('customer', 'internal')
- display_name text
- phone text nullable
- status enum('invited', 'active', 'disabled')
- last_login_at timestamptz nullable
- created_at timestamptz
- updated_at timestamptz

audit_events
- id uuid primary key
- organisation_id uuid nullable
- actor_user_id uuid nullable
- actor_type text
- action text
- resource_type text
- resource_id text nullable
- summary jsonb
- reason text nullable
- trace_id text
- created_at timestamptz
```

Do not put roles directly on `profiles`; roles belong to internal-role mappings or organisation memberships.

### API/server actions

```text
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/forgot-password
POST /api/auth/reset-password
GET  /auth/callback
GET  /api/auth/session
```

If server actions are used instead of REST endpoints, keep equivalent typed input/output contracts.

### Login response contract

Return only the state the UI needs:

```json
{
  "next": "/app"
}
```

Error responses use a safe common envelope:

```json
{
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Email or password is incorrect."
  }
}
```

### Tests

- Successful customer login redirects to `/app`.
- Successful internal login with valid MFA redirects to `/admin`.
- Invalid credentials return a generic error.
- Unverified email enters the verification flow.
- Disabled users cannot create a valid application session.
- Password-reset tokens expire and cannot be reused.
- Protected routes redirect unauthenticated users to login.
- Customer sessions cannot open internal routes.
- Cookies have appropriate secure, HTTP-only, same-site and expiry behaviour.
- Rate limiting activates after the approved failure threshold.
- Authentication errors do not leak stack traces or account existence.

### Exit gate

Login, logout, verification, recovery, session refresh and route protection pass in staging. Do not begin dashboard development before this gate passes.

## 6. Step 2 — organisations, membership, RBAC and RLS

### Goal

Determine which tenant a signed-in user may access and enforce that boundary independently of frontend routing.

### Frontend tasks

- Organisation creation form for a new super admin
- Organisation selector for a user with multiple memberships
- Access-denied page
- Users and access list shell
- Invite-user dialog
- Role selector built from server-returned allowed roles
- Current organisation switcher in the application header

### Backend tasks

- Create organisations and first-user super-admin membership transactionally.
- Implement capability-based permissions.
- Add default customer roles and internal roles.
- Add membership status, team/location/channel scope, invitation and revocation.
- Add organisation selection to the verified session context.
- Implement RLS for every tenant-owned table.
- Add a service-layer authorisation helper that checks capability and scope.
- Audit membership, permission, invitation and organisation-selection changes.

### Core tables

```text
organisations
organisation_locations
organisation_users
roles
permissions
role_permissions
organisation_user_roles
organisation_user_scopes
invitations
internal_user_roles
```

### Required permission examples

```text
organisation.read
organisation.update
users.read
users.invite
users.revoke
roles.assign
billing.read
billing.manage
integrations.read
integrations.manage
inbox.read
inbox.reply
inbox.assign
agents.read
agents.manage
agents.publish
reviews.read
reviews.reply
reviews.publish
analytics.read
exports.create
services.pause
services.resume
```

### API

```text
POST   /api/organisations
GET    /api/organisations
POST   /api/session/organisation
GET    /api/organisations/current
GET    /api/organisations/current/users
POST   /api/organisations/current/invitations
PATCH  /api/organisations/current/users/:userId
DELETE /api/organisations/current/users/:userId
GET    /api/permissions/me
```

### Tests

- A new user can create one organisation and becomes its super admin.
- A user can access only organisations with an active membership.
- Changing a browser-supplied organisation ID cannot cross tenants.
- UI, API, database, storage and realtime tenant-isolation tests pass.
- An operator cannot access billing or agent publication.
- A billing contact cannot read conversation content.
- A revoked user loses access on the next protected request/realtime check.
- Permission changes produce audit records.

### Exit gate

Two seeded tenants pass the full cross-tenant isolation suite, including direct API and database-policy attempts.

## 7. Step 3 — customer application shell and real home dashboard

### Goal

Give authenticated customer users a usable application frame and a home page backed by real tenant state.

### Frontend tasks

- Responsive application sidebar/top bar
- Organisation switcher
- Current user menu and logout
- Navigation filtered by permissions
- Notification/alert area
- Onboarding-progress card
- Organisation health summary
- Empty KPI cards for conversations, leads, reputation, usage and integrations
- Data-freshness labels
- Loading, no-data, permission-denied, delayed-data and service-error states

### Backend tasks

- Create a tenant home-summary query/service.
- Return readiness, lifecycle, enabled modules, alerts and safe empty metrics.
- Create a notification model.
- Cache only tenant-safe aggregate responses.
- Add permission-aware response shaping.

### API

```text
GET /api/home/summary
GET /api/notifications
POST /api/notifications/:id/read
```

### Tests

- Navigation changes correctly by permission.
- Every card shows a useful empty state before channels are connected.
- One tenant cannot receive another tenant's cached summary.
- Data freshness is visible.
- Dashboard remains usable on tablet and mobile web.

### Exit gate

A signed-in user reaches a permission-correct application home, sees real organisation state and can log out.

## 8. Step 4 — commercial onboarding, plans and Stripe

### Goal

Allow a super admin to create a commercially valid tenant and reach Ready for testing.

### Frontend sequence

1. Welcome and organisation details
2. Plan selection
3. Secure Stripe payment step
4. Terms/privacy acceptance
5. Business profile
6. Locations and trading hours
7. Services and FAQs
8. Brand/tone basics
9. Escalation contacts
10. Integration/channel checklist
11. User invitation
12. Readiness summary and blockers

### Backend tasks

- Create versioned plans, prices and entitlements.
- Create Stripe customer/checkout/subscription mappings.
- Validate signed Stripe webhooks.
- Implement idempotent webhook processing.
- Implement the full tenant lifecycle state machine.
- Save onboarding by section, not only at final submit.
- Calculate readiness from explicit rules.
- Prevent production activation when required billing/setup rules fail.
- Record accepted terms/privacy version and timestamp.

### Tables

```text
plans
plan_versions
entitlements
subscriptions
billing_profiles
organisation_terms_acceptance
onboarding_sections
onboarding_blockers
organisation_services
organisation_hours
```

### API/events

```text
GET   /api/plans
POST  /api/billing/checkout-session
POST  /api/webhooks/stripe
GET   /api/onboarding
PATCH /api/onboarding/:section
GET   /api/onboarding/readiness
POST  /api/onboarding/submit-for-approval

Event: billing.subscription.updated
Event: organisation.lifecycle.changed
Event: onboarding.readiness.changed
```

### Tests

- Webhooks with invalid signatures fail.
- Duplicate Stripe events do not duplicate subscriptions or transitions.
- Payment-pending tenants cannot activate production services.
- Entitlements are configuration data and version-aware.
- Onboarding resumes at the last incomplete section.
- Required blockers are clear and deterministic.

### Exit gate

A new super admin can register, select a plan, add a payment method, configure the business, invite a user and reach Ready for testing.

## 9. Step 5 — integration centre foundation

### Goal

Create one reusable connector framework before building individual vendor connections.

### Frontend tasks

- Connector catalogue
- Category, availability and search filters
- Connection prerequisites
- Permissions requested
- Connect/reconnect/test/disconnect actions
- Status: Not connected, Connecting, Connected, Warning, Error, Expired, Paused
- Last successful event and data freshness
- Recent safe error summaries
- Secret fingerprint/last-used/rotation UI for approved API-key connectors

### Backend tasks

- Define a connector adapter interface.
- Implement OAuth state/PKCE handling where supported.
- Store encrypted token/secret references.
- Implement token refresh and revocation.
- Implement connection tests and health checks.
- Create webhook endpoint registration and provider-to-tenant mapping.
- Add idempotency, retry, dead-letter and safe replay foundations.
- Prevent arbitrary user-supplied endpoints or unrestricted API execution.

### Tables

```text
integration_catalogue
integrations
integration_secret_references
integration_permissions
integration_events
integration_health_checks
webhook_receipts
dead_letter_events
external_record_mappings
```

### Connector interface

```text
connect()
handleCallback()
refreshCredentials()
testConnection()
getHealth()
handleWebhook()
executeAllowedAction()
disconnect()
```

### Tests

- OAuth state cannot be reused or moved between tenants.
- Secrets never return to the browser after submission.
- Disconnect revokes access where supported and disables actions.
- Health errors are visible without exposing tokens or sensitive payloads.
- Webhook receipts are signature-checked and idempotent.

### Exit gate

One test connector can connect, test, display health, receive an idempotent webhook and disconnect using the common framework.

## 10. Step 6 — unified inbox and contacts core

### Goal

Implement the channel-independent data and UI before connecting more providers.

### Frontend tasks

- Inbox queue and filters
- Conversation view
- Message composer
- Delivery-state indicators
- Assignment and team selection
- Internal notes
- Tags, priority, follow-up and resolution
- Contact profile and channel identities
- Unified chronological customer timeline
- AI/human author label
- Handover and response-mode controls
- Paginated history and search

### Backend tasks

- Define the normalised channel-event schema.
- Implement contacts and separate channel identities.
- Use deterministic identity matching first.
- Create a review queue for uncertain merges.
- Implement conversations, messages, assignment, notes and tasks.
- Implement realtime events scoped by tenant and inbox.
- Add search indexes and cursor pagination.
- Store provider source IDs for idempotency.

### Tables

```text
channels
inboxes
contacts
contact_channels
contact_merge_candidates
conversations
messages
message_delivery_events
assignments
internal_notes
tags
conversation_tags
tasks
timeline_events
```

### API/realtime

```text
GET   /api/inbox/conversations
GET   /api/inbox/conversations/:id
POST  /api/inbox/conversations/:id/messages
PATCH /api/inbox/conversations/:id
POST  /api/inbox/conversations/:id/assign
POST  /api/inbox/conversations/:id/notes
GET   /api/contacts/:id/timeline
POST  /api/contacts/merge-review

Realtime: conversation.created
Realtime: message.created
Realtime: message.delivery_updated
Realtime: conversation.assigned
```

### Tests

- Filters, pagination and unread state remain consistent.
- An operator cannot open conversations outside their assigned scope.
- Uncertain identities are not automatically merged.
- Messages clearly show pending, sent, delivered and failed states.
- Realtime subscriptions cannot cross tenant boundaries.
- Provider duplicate events do not create duplicate messages.

### Exit gate

Seeded channel events create contacts/conversations and can be operated entirely from the VicAI UI.

## 11. Step 7 — website chat vertical slice

### Frontend tasks

- Widget installation instructions
- Allowed-domain configuration
- Test mode and preview
- Widget colour/logo/greeting options within approved design controls
- Website-chat messages in the inbox

### Backend tasks

- Issue tenant/channel-scoped public widget configuration.
- Validate allowed origins/domains.
- Add abuse protection and rate limiting.
- Create anonymous visitor/session identifiers.
- Normalise widget messages into the inbox.
- Add human/AI routing state.
- Record source URL and campaign fields safely.

### Tests

- Widget works only on allowed domains.
- Public requests cannot choose another tenant.
- Abuse limits activate without blocking normal conversation.
- Test-mode messages are visibly separated from production.
- Website chat produces a complete conversation timeline.

### Exit gate

A test-site visitor starts a chat and an authorised VicAI user receives, assigns and replies to it.

## 12. Step 8 — SMS vertical slice

### Frontend tasks

- SMS number/sender connection status
- SMS messages in conversation view
- Character/segment estimate
- Delivery-state and failure UI
- Opt-out status and blocked-send explanation

### Backend tasks

- Connect ClickSend number/sender.
- Validate inbound and delivery webhooks.
- Send through the server-side connector.
- Store provider message ID, direction, segments and delivery state.
- Detect and enforce opt-out/opt-in keywords and policy.
- Create idempotent usage events per segment.
- Add retry rules that do not duplicate outbound messages.

### Tests

- Inbound SMS reaches the correct tenant/contact.
- Outbound SMS receives delivery updates.
- Duplicate delivery webhooks do not duplicate usage.
- An opted-out contact cannot receive prohibited outbound SMS.
- Failed messages remain visible and retryable where safe.

### Exit gate

Two-way SMS works end to end with delivery receipts, opt-out handling and usage events.

## 13. Step 9 — voice AI vertical slice

### Frontend tasks

- Voice number status and routing configuration
- Transfer target and business-hours behaviour
- Test-call action
- Call record, outcome, transcript and recording state
- Voice usage display
- Human-handover context

### Backend tasks

- Connect Telnyx number/SIP routing to Retell.
- Validate all call webhooks.
- Map call/provider/agent IDs to the tenant.
- Store start/end, direction, outcome, transfer and status.
- Store transcript references and approved recording references.
- Enforce recording/consent configuration.
- Implement low-latency approved tools directly, excluding n8n from the synchronous path.
- Create voice and AI usage events with provider IDs.

### Tests

- Inbound call reaches the correct agent.
- Transfer uses the configured target and preserves context.
- Transcript and outcome appear after completion.
- Call recording follows the approved setting.
- Duplicate callbacks do not duplicate calls or minutes.
- Provider failure follows the configured safe fallback.

### Exit gate

A live test call completes, transfers when required, appears in the timeline and produces reconciliable usage.

## 14. Step 10 — one email provider vertical slice

### Frontend tasks

- Connect Microsoft 365 or Gmail
- Select approved mailbox
- Show permissions, sync state and token health
- Email messages and reply composer in the inbox
- Disconnect/reconnect experience

### Backend tasks

- Implement the selected provider's OAuth flow.
- Subscribe to or poll approved mailbox events.
- Normalise email threads/messages.
- Preserve reply headers/thread mapping.
- Send replies through the provider.
- Refresh/revoke tokens.
- Record provider IDs, status and safe errors.

### Tests

- Only selected mailboxes are accessible.
- Inbound messages map to the correct tenant and thread.
- Replies remain in the provider thread.
- Revoked credentials block access and create a visible health warning.
- Attachments follow tenant storage and content restrictions.

### Exit gate

One supported mailbox can connect, receive, display, reply and disconnect through VicAI.

## 15. Step 11 — AI agents, knowledge and policy

### Frontend tasks

- Agent list and status
- Identity/purpose/channel configuration
- Brand and tone settings
- Knowledge-source upload/list/status
- Goals, allowed actions and handover rules
- Human-only, AI-draft, conditional auto-send, AI-first and paused modes
- Scenario runner and test chat/call
- Draft/publish/rollback/version history
- Feedback on accepted, edited and rejected drafts

### Backend tasks

- Create agent and immutable published-version models.
- Process tenant-isolated knowledge sources.
- Implement retrieval with tenant filters.
- Create the VicAI model gateway.
- Build prompt/policy composition from versioned configuration.
- Define allowed tools with schema validation and authorisation.
- Enforce confidence, intent, hours, restricted topics and handover rules.
- Audit input category, decision, selected policy/version, action and result without unnecessarily storing sensitive prompt content.
- Meter model requests and AI actions.

### Tables

```text
agents
agent_versions
agent_channel_assignments
agent_policies
knowledge_sources
knowledge_documents
knowledge_chunks
tool_definitions
agent_tools
agent_test_runs
ai_decisions
ai_feedback
```

### Tests

- Retrieval cannot return another tenant's knowledge.
- Draft mode never sends automatically.
- Auto-send requires every configured condition to pass.
- Restricted scenarios hand over with a visible reason.
- A tool cannot execute outside its schema or user/agent permission.
- Failed external writes are never reported as successful.
- Published versions can be rolled back and are fully audited.

### Exit gate

An admin can configure, test, publish and roll back an agent; an operator can review a draft; and a forced-escalation scenario hands over correctly.

## 16. Step 12 — customer analytics and reporting

### Frontend tasks

- Executive summary
- Conversation performance
- Channel mix
- AI quality
- Reputation summary
- Usage summary
- Integration health
- Time, location, channel and agent filters
- Data-freshness labels
- Authorised CSV export

### Backend tasks

- Create operational event facts.
- Add queued hourly/daily aggregates.
- Keep raw events separate from aggregates.
- Build permission-scoped reporting queries.
- Add freshness and last-computed metadata.
- Audit exports.

### Tests

- Sample aggregate figures reconcile to raw events.
- Time-zone boundaries use the organisation's configured timezone.
- Filters do not leak out-of-scope locations or agents.
- Delayed aggregation is clearly labelled.
- Exports obey permission and scope.

### Exit gate

The dashboard shows real P0 channel metrics with verified sample reconciliation and freshness.

## 17. Step 13 — reputation management

### Frontend tasks

- Google account/location connection
- Review list and filters
- Rating/reply-rate/trend cards
- Review details and internal comments
- AI draft, edit, approve, reject and publish
- Priority task for negative reviews
- Review-request configuration
- Manual/import fallback state

### Backend tasks

- Connect Google Business Profile when approval is available.
- Store source review/location IDs.
- Classify sentiment/themes.
- Generate controlled reply drafts.
- Block automatic public replies for one-to-three-star reviews.
- Publish only after permission and approval.
- Implement review-request consent, suppression and frequency caps.
- Support an honest manual/import fallback without pretending publishing succeeded.

### Tests

- Reviews map to the correct tenant/location.
- Negative reviews always create a priority workflow.
- Unauthorised users cannot approve or publish.
- Provider failure remains visible and retryable.
- Review requests respect consent and frequency rules.

### Exit gate

Positive and negative review journeys work with approval, audit, metrics and the documented API fallback.

## 18. Step 14 — usage, entitlements and billing readiness

### Frontend tasks

- Current plan and entitlements
- Current-period usage by dimension
- Included allowance, percentage used and estimate
- Data-freshness and reconciliation warnings
- Payment method summary and renewal
- Invoice/receipt links
- Billing contact and authorised export

### Backend tasks

- Create append-only usage-event types and ledger.
- Keep vendor quantity, normalised quantity and billable quantity separate.
- Store idempotency/provider IDs.
- Add versioned cost/rate catalogue.
- Reconcile vendor reports daily.
- Add adjustments rather than editing raw events.
- Close invoice periods.
- Apply entitlements/overage rules.
- Validate and freeze immutable invoice snapshots.
- Export invoice-ready CSV.

### Tables

```text
usage_event_types
usage_events
usage_adjustments
usage_aggregates
cost_catalogue
invoice_periods
invoice_snapshots
invoice_snapshot_lines
reconciliation_runs
reconciliation_exceptions
```

### Tests

- Duplicate provider IDs cannot double bill.
- Historical usage retains its pricing/cost version.
- Adjustments require reason and permission.
- Frozen snapshots cannot be edited.
- Dashboard totals reconcile to snapshot inputs.
- Billing contacts cannot read message content.

### Exit gate

Finance can validate one sample period, resolve/override warnings with reason, freeze a snapshot and export invoice-ready CSV.

## 19. Step 15 — internal admin portal

### Frontend tasks

- Tenant portfolio table and filters
- Tenant detail summary
- Lifecycle, plan and entitlement view
- Consumption and billing readiness
- Channel/integration/AI health
- Customer activity and inbox backlog
- Incidents and support ownership
- Audit search
- Role-sensitive content visibility

### Backend tasks

- Create restricted internal views/services.
- Separate operations, finance, support and analyst permissions.
- Prevent finance/read-only roles from receiving message content by default.
- Create transparent health components.
- Create incident and ownership models.
- Add safe integration diagnostics and eligible event replay.

### Tests

- Internal role restrictions are enforced server-side.
- Finance sees commercial data without conversation content.
- Analysts receive aggregated/authorised views.
- Event replay is idempotent and permissioned.
- Admin access creates audit events.

### Exit gate

Authorised VicAI staff can understand and operate the lighthouse tenant without direct database or vendor-dashboard access for normal work.

## 20. Step 16 — service controls and support access

### Frontend tasks

- Pause/resume control by service scope
- Impact preview
- Required reason and effective time
- Customer-notification option
- Current service-state banner
- Resume health-check results
- Time-limited support-access request and active banner

### Backend tasks

- Create service-state policy evaluation.
- Enforce state before outbound/AI/provider actions.
- Support all, outbound, AI auto-send, voice, SMS, email, agent and integration scope.
- Store actor, reason, impact selection and timestamps.
- Require health/billing checks before resume.
- Create time-limited, reason-coded support sessions.
- Show support-access state to the customer.
- Audit all support activity.

### Tests

- Pausing SMS blocks only the selected scope.
- Pausing AI auto-send leaves the human inbox usable.
- Resume fails safely when billing/credentials are unhealthy.
- Support access expires automatically.
- Support access cannot bypass tenant or capability policy.
- Every state/support action is audited.

### Exit gate

Operations can preview, pause and safely resume a service, while a customer can see the state and any active support access.

## 21. Step 17 — hardening and lighthouse launch

### Frontend completion

- Responsive review of all critical flows
- Keyboard and screen-reader review
- Complete loading, empty, error, offline/delayed and permission-denied states
- Safe confirmation for destructive/privileged actions
- Status/incident banner
- User guidance and support entry points

### Backend/platform completion

- Full end-to-end suite
- RLS/API/storage/realtime isolation suite
- Authentication, privilege, CSRF, CSP, rate-limit and secret-exposure tests
- Webhook replay and idempotency tests
- Vendor outage and token-expiry drills
- Performance tests
- Backup and restore rehearsal
- Monitoring, alerts and incident runbooks
- Production migrations and rollback
- Retention, export and offboarding checks
- Lighthouse configuration and production smoke tests

### Final launch journey

```text
Register
→ verify email
→ create organisation
→ select plan/add payment
→ configure business
→ connect required channels
→ create/test AI agent
→ invite user
→ request activation
→ VicAI readiness approval
→ production test
→ controlled go-live
```

### Exit gate

Launch only when the go-live checklist in `VicAI_Phase_Wise_Implementation_Plan.md` passes. Week 16 alone is not approval to launch.

## 22. Step 18 — P1 expansion after P0 stability

Implement P1 in this order unless the lighthouse contract changes the priority:

1. ServiceM8 connector
2. Second email provider
3. Xero draft invoice API
4. Facebook Messenger and Instagram
5. WhatsApp
6. Multi-location reputation
7. Ranking provider
8. Advanced custom roles
9. Automated overage handling
10. Richer analytics

Each connector must reuse the Step 5 integration contract and pass connect, permissions, health, action, webhook, retry, disconnect, audit and usage tests.

## 23. Marketing homepage implementation

The new `index.html` is a standalone, responsive implementation inspired by the reference website's information flow:

- outcome-led hero;
- immediate product interface proof;
- connected channel strip;
- attract/capture/convert/retain positioning;
- interactive platform feature tabs;
- step-by-step customer journey;
- industry relevance;
- control/security section;
- FAQ and focused demo CTA.

It deliberately avoids:

- copying Podium's wording, images or branded visual assets;
- claiming Podium's customer counts or performance statistics;
- publishing the unresolved VicAI plan prices;
- presenting P1 functionality as already production-ready.

### Homepage backend upgrade

The current static form prepares an email and stores no data. When the application backend exists, replace it with:

```text
POST /api/public/demo-requests
```

The production endpoint must include:

- schema validation;
- IP and email rate limiting;
- bot protection;
- consent/privacy acknowledgement;
- safe CRM or notification delivery;
- structured logging without message-body leakage;
- duplicate/spam handling;
- success/error UI;
- monitoring and alerting.

Suggested table if leads are stored:

```text
demo_requests
- id
- name
- email
- company
- business_type
- message
- consent_version
- source
- status
- created_at
```

Restrict access to authorised internal sales/operations users and define a retention period before storing public enquiries.

## 24. Branch and pull-request order

Keep early pull requests small and reviewable:

```text
PR 01: repository, CI and environment validation
PR 02: shared UI tokens and authentication layout
PR 03: backend login/session/logout
PR 04: login/recovery/verification UI
PR 05: protected route middleware and auth tests
PR 06: organisation/membership schema and RLS
PR 07: organisation setup and selection UI
PR 08: permissions and invitation flow
PR 09: customer app shell and home summary
PR 10+: one PR group per approved vertical slice
```

Do not combine authentication, billing, inbox and AI into one large initial pull request.

## 25. Definition of Done for every implementation step

A step is not complete until:

- database migrations apply cleanly from an empty database;
- RLS and service-layer authorisation pass;
- API/event contracts are typed and documented;
- success, loading, empty, denied and failure UI states work;
- external operations are idempotent where required;
- audit and usage events are created where required;
- logs and errors contain trace IDs but no secrets;
- automated unit, integration and end-to-end tests pass;
- changed screens meet keyboard, focus, contrast and responsive requirements;
- monitoring covers new external dependencies;
- staging demonstration passes the written exit gate;
- deferred behaviour and known limitations are recorded.

## 26. Immediate development checklist

Complete these items first:

- [ ] Confirm repository strategy and team responsibilities.
- [ ] Create the applications and shared packages.
- [ ] Configure Supabase development/staging projects.
- [ ] Add migrations, type generation, CI and environment validation.
- [ ] Build the shared authentication layout and components.
- [ ] Implement backend login/session/logout.
- [ ] Build `/login`, `/forgot-password`, `/reset-password`, `/verify-email` and `/auth/callback`.
- [ ] Add protected-route middleware.
- [ ] Add internal MFA flow.
- [ ] Write authentication integration and browser tests.
- [ ] Demonstrate authentication in staging.
- [ ] Begin organisation membership, RBAC and RLS only after the authentication gate passes.
