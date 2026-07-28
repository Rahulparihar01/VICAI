# VicAI — Delivery Phases: P0, P1, P2

**Source:** VicAI MVP Developer Build Brief v3.0, July 2026 (Sections 7.3, 17.1, 17.2, 18, 19)
**Purpose:** A checkable, phase-gated work plan. Architecture must support the full product from day one; these phases control what is *switched on* and in what order, against the A$30,000 build budget.

---

## P0 — Investor / Lighthouse Release (Build First)

The minimum credible product: one lighthouse tenant can onboard, operate, and be demoed to investors.

### Portals & Branding
- [ ] Custom VicAI customer portal (branded, no visible third-party UI)
- [ ] Custom VicAI internal admin portal
- [ ] Shared design system across both

### Onboarding & Identity
- [ ] Tenant registration, organisation creation, super admin assignment
- [ ] Plan selection (Starter / Growth / Pro)
- [ ] Stripe payment method setup (hosted/embedded — no raw card storage)
- [ ] RBAC foundation: roles, organisation_users mapping, capability-based permissions
- [ ] Onboarding checklist + state model (Created → Payment pending → Configuring → Ready for testing → Active…)

### Channels (P0 set only)
- [ ] Voice (Telnyx + Retell)
- [ ] SMS (ClickSend)
- [ ] Website chat widget
- [ ] One email provider — Microsoft 365 **or** Gmail (decision pending, §19)

### Unified Inbox
- [ ] Channel/status filters, assignment, internal notes, tags
- [ ] Contact timeline, transcripts, delivery status
- [ ] Human replies with visible AI/human authorship

### AI Agents
- [ ] Agent configuration (identity, brand/tone, knowledge, goals)
- [ ] Draft mode and conditional/controlled auto-send mode
- [ ] Basic testing (scenario/test chat/test call)

### Dashboards & Usage
- [ ] Core/executive-level dashboard
- [ ] Raw usage event capture (append-only, idempotent, tenant-attributed)
- [ ] Internal tenant health view
- [ ] Service pause/resume controls with audit trail

### Reputation
- [ ] Google Business Profile review dashboard + AI reply workflow (where API approval exists)
- [ ] Manual/import fallback if API access isn't ready

### Billing & Export
- [ ] Stripe subscription/payment state mapped to tenant lifecycle
- [ ] CSV usage/invoice export
- [ ] Xero API — **optional at P0**, may defer to P1

### P0 Definition of Done (cross-check against §18 Acceptance Criteria)
- [ ] Branding: no visible third-party redirect for normal work
- [ ] Tenant isolation enforced (UI, API, DB RLS)
- [ ] Full self-onboarding path works end to end
- [ ] RBAC enforced in UI and API
- [ ] Inbox: receive/read/assign/reply with delivery status
- [ ] Voice: call → AI → transcript/outcome → usage event
- [ ] AI controls: human-only/draft/auto-send + publish/rollback
- [ ] Usage: deduplicated, tenant-attributed, visible in both portals
- [ ] Billing: invoice-ready snapshot + export works
- [ ] Admin health: tier, lifecycle, consumption, incidents visible
- [ ] Service control: pause/resume with impact preview + audit
- [ ] Audit: privileged actions and AI config changes traceable
- [ ] Failure handling: failed events visible/retryable, never silently marked successful

---

## P1 — After P0 Stability, or Where Lighthouse Requires It

Expands channel and integration breadth once the P0 core is proven stable.

- [ ] ServiceM8 connector (customer search/create, job/quote request, notes, status)
- [ ] Microsoft 365 **and** Google Workspace dual-provider email support
- [ ] Xero draft invoice API (if not already done at P0)
- [ ] Instagram production connection (post Meta approval)
- [ ] Facebook Messenger production connection (post Meta approval)
- [ ] WhatsApp session messages + approved templates (post business verification)
- [ ] Ranking/visibility provider integration (or confirm manual entry is sufficient — see §19)
- [ ] Richer reputation analytics (trends, sentiment themes, location comparison)
- [ ] Advanced custom roles (beyond base permission catalogue)
- [ ] Multi-location comparison views
- [ ] Automated overage billing/calculation

---

## P2 — Demand-Gated (Build Only Against Signed Pipeline)

Explicitly not committed for the lighthouse/investor release. Only build if a signed customer or clear pipeline demand requires it.

- [ ] Additional CRM/business-management system connectors beyond ServiceM8 (§7.3)
- [ ] Any further per-vendor cost catalogue refinements beyond what P0/P1 requires operationally

*(The brief does not spell out an extensive P2 list — it is intentionally left open and demand-driven. Treat anything not explicitly in P0/P1 above, and not in the "explicitly out of scope" list below, as P2-by-default.)*

---

## Explicitly Out of Scope for the Entire MVP (Not a Phase — Do Not Build)

Per §2.2, these are excluded from P0, P1, and P2 alike unless a future scope change is agreed:

- Native iOS or Android apps
- Full CRM/ERP/field-service/practice-management/accounting replacement
- General-purpose no-code workflow builder
- Healthcare triage, diagnosis, treatment recommendations, clinical notes, patient records
- Automatic public replies to negative reviews without customer-approved rules
- Unrestricted customer-supplied code or arbitrary API execution
- Google/social-media scraping (approved APIs only)
- Enterprise-grade regulatory certification

---

## Open Decisions to Resolve Before/During P0 (§19)

These affect exact P0 scope and should be settled early, ideally before sprint planning:

1. Exact entitlements (usage/users/locations/agents/integrations) per plan tier
2. Which email provider is P0: Microsoft 365, Gmail, or both
3. Is Xero API mandatory for release 1, or is CSV export acceptable
4. Can customers self-pause services, or only VicAI internal admins
5. Grace period and behavior after Stripe payment failure
6. Call recording default: on, opt-in, or off for the lighthouse client
7. Overage pricing model: pass-through, markup, or bundled
8. First approved ranking data provider, or is manual entry sufficient for MVP

---

## Suggested Sequencing for Starting Work

1. **Foundation** — design system, tenant model, auth, RBAC, environments, CI/CD
2. **Commercial onboarding** — plans, Stripe, org setup, checklist, activation states
3. **Channel core** — voice, SMS, website chat, email, unified inbox, contacts, realtime
4. **AI and knowledge** — agent configuration, knowledge, drafting, tool policies, tests
5. **Customer portal analytics** — dashboard, usage, integrations, reviews, exports
6. **Admin operations** — tenant health, usage, plans, controls, incidents, billing readiness
7. **Business integrations** — ServiceM8, GBP, Meta channels, Xero draft invoices *(P1)*
8. **Lighthouse hardening** — onboarding polish, test scenarios, monitoring, backup, support process *(pre-launch)*

This mirrors the work-package sequence in §17 of the brief and lines up P0 build order with dependency order (you can't build AI agents before RBAC/tenant model exists, etc.).