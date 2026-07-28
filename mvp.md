# VicAI — Full MVP Scope (Section 1–2) vs. P0 Delivery Scope (Section 17.1)

**Source:** VicAI MVP Developer Build Brief v3.0, July 2026
**Purpose:** Clarify what "MVP" means as originally scoped (Sections 1–2) versus what is actually buildable first under the A$30,000 budget constraint (Section 17.1 — P0 / Investor-Lighthouse Release).

---

## 1. The Core Difference

- **Sections 1–2** define the *full, aspirational MVP* — everything required for VicAI to be a credible multi-tenant product. No budget lens is applied here.
- **Section 17.1 (P0)** is the *budget-gated release* — the subset that is actually buildable first, with the remainder sequenced into P1/P2.

The brief itself states this directly:

> "The requested A$30,000 MVP build budget is tight for the full specification... delivery must be gated into P0, P1 and P2."

Nothing in P0 contradicts Section 2 — it is a **sequencing decision**, not a redefinition of the product. The architecture must still support full Section 2 scope; P0 just determines what ships first.

---

## 2. Item-by-Item Comparison

| Requirement (from §2 "Must build") | In Full MVP (§1–2)? | In P0 (§17.1)? | Status |
|---|---|---|---|
| Custom branded customer portal | ✅ Required | ✅ Included | Match |
| Custom branded internal admin portal | ✅ Required | ✅ Included | Match |
| Self-service registration, Stripe payment, onboarding tracking | ✅ Required | ✅ Included | Match |
| Multi-tenant identity, RBAC | ✅ Required | ✅ Included (foundation only) | Partial — custom role catalogue is P1 |
| Unified inbox across channels | ✅ Required (all channels) | ✅ Included, narrowed | **Reduced** — voice, SMS, web chat, one email only |
| Voice AI | ✅ Required | ✅ Included | Match |
| SMS chatbot | ✅ Required | ✅ Included | Match |
| Website chatbot | ✅ Required | ✅ Included | Match |
| Email AI | ✅ Required | ✅ Included | **Reduced** — one provider only, not both M365 + Google |
| WhatsApp | ✅ Required | ❌ Not included | **Deferred to P1** |
| Instagram | ✅ Required | ❌ Not included | **Deferred to P1** |
| Facebook Messenger | ✅ Required | ❌ Not included | **Deferred to P1** |
| System connection centre (M365, Google, Meta, GBP, CRM) | ✅ Required (all) | ⚠️ Partial | GBP (reviews) included; M365/Google/Meta/CRM → P1 |
| AI agent creation, config, testing | ✅ Required | ✅ Included | Match |
| Full dashboards (§5.2 depth) | ✅ Required, detailed | ⚠️ Reduced | Core dashboards only, not full analytics depth |
| Reputation management | ✅ Required, full workflow | ⚠️ Reduced | Google reviews + manual fallback; ranking/visibility → P1 |
| Internal tenant health / service control | ✅ Required | ✅ Included | Match |
| Usage metering, CSV export | ✅ Required | ✅ Included | Match |
| Xero invoice automation | ✅ Required | ❌ Optional/deferred | P0 may ship with CSV fallback only |
| Pause/resume tenant services | ✅ Required | ✅ Included | Match |
| Audit logs | ✅ Required | ✅ Included | Match |
| ServiceM8 / business-system integration | ✅ Required (CRM connectors) | ❌ Not included | **Deferred to P1** |
| Advanced custom roles, multi-location comparison | ✅ Required | ❌ Not included | **Deferred to P1** |
| Automated overage billing | Implied in usage/billing reqs | ❌ Not included | **Deferred to P1** |

---

## 3. What P0 Keeps Intact

- Both portals (customer + admin), full branding integrity
- RBAC foundation (roles, org membership, capability-based permissions)
- Stripe onboarding flow and lifecycle state model
- Voice + SMS + web chat + one email channel
- Unified inbox core functions (assignment, notes, status, transcripts)
- AI agent configuration with draft / controlled auto-send modes
- Raw usage capture, internal tenant health view, service pause/resume
- CSV billing/usage export

## 4. What P0 Strips Out or Shrinks

| Area | Full MVP (§1–2) | P0 Reality |
|---|---|---|
| Channel breadth | 7 channels (voice, SMS, web, email, WhatsApp, Instagram, Facebook) | 4 channels only |
| Integration breadth | M365, Google, Meta, GBP, CRM, business-management systems | GBP only confirmed; rest → P1 |
| Reputation depth | Full workflow incl. ranking/visibility tracking, multi-location comparison | Review dashboard + reply workflow only |
| Xero | Required | Optional; CSV fallback acceptable |
| RBAC depth | Custom roles, location/team scoping | Basic roles only |
| Analytics depth | Full KPI set (§5.2) | Core dashboards only |

---

## 5. Cross-Check: P0 Against Acceptance Criteria (§18)

P0 should satisfy these criteria specifically before being considered "done":

- **Branding** — no visible third-party redirect during normal use
- **Tenant isolation** — enforced in UI, API, and database (RLS)
- **Self-onboarding** — register → plan → payment → business config → connect → test → invite
- **RBAC** — enforced in both UI and API
- **Inbox** — receive / read / assign / reply with delivery status
- **Voice** — call → AI → transcript/outcome → usage event
- **AI controls** — human-only / draft / auto-send modes, publish/rollback
- **Usage** — deduplicated, tenant-attributed, visible in both portals
- **Billing** — Stripe state mapped to tenant lifecycle; invoice-ready snapshot + export
- **Admin health** — tier, lifecycle, consumption, health, incidents all visible
- **Service control** — pause/resume with impact preview + audit trail
- **Audit** — privileged actions and AI configuration changes traceable
- **Failure handling** — failed events visible/retryable, never silently marked successful

---

## 6. Open Decisions That Affect P0 Scope (§19)

These must be resolved before P0 scope can be fully locked:

1. Exact plan entitlements (Starter / Growth / Pro) — not yet approved
2. Which email provider is P0 — Microsoft 365, Gmail, or both
3. Is Xero API mandatory for release 1, or is CSV export sufficient
4. Can customers self-pause services, or only VicAI internal admins
5. Grace period / behavior after Stripe payment failure
6. Call recording default — on, opt-in, or off for the lighthouse client
7. Overage pricing model — pass-through, markup, or bundled
8. First approved ranking data provider, or is manual entry sufficient for MVP

---

## 7. Bottom Line

Section 2 defines **what VicAI is as a product**. P0 defines **what proves the product works** for one lighthouse customer and an investor demo — same architecture, same data model, same non-negotiable principles (no visible third-party tools, tenant isolation, full audit trail) — just fewer channels and integrations switched on at launch.