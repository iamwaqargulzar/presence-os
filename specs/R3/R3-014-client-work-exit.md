# R3-014 — Client-Work Readiness and R3 Exit

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Prove with evidence that R3 works end to end and fails closed, and confirm every condition the documents set before real client data and real client accounts are used. Then run the first real tenant, an operator-owned one, before any client.

## Why now
R3 is the first release used for real client work. After this point a mistake is public: a wrong post on a client's page, a broken client site, or a lost client record.

## Context / linked docs / ADRs
- [R3 README](README.md) and every R3 task contract
- [Gates](../../docs/delivery/gates.md) (sections 4 to 6)
- [Testing strategy](../../docs/delivery/testing-strategy.md)
- [Backup and disaster recovery](../../docs/infrastructure/backup-disaster-recovery.md)
- [Runbook: backup restore drill](../../docs/runbooks/backup-restore-drill.md)
- [Runbook: security incident](../../docs/runbooks/security-incident.md)
- [Runbook: tenant offboarding](../../docs/runbooks/tenant-offboarding.md)
- [Service levels and SLOs](../../docs/operations/service-levels-and-slo.md)
- [Assumptions and open questions](../../docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md) (all entries tagged R3)
- [R2 exit](../R2/R2-017-intelligence-exit.md)
- ADR-0008, ADR-0015, ADR-0017, ADR-0030

## Depends on
- R3-001 to R3-013.

## Invariants
- evidence, not declaration, closes the release;
- release blockers: cross-tenant access, unauthorised side effect, broken rollback, secret exposure, duplicate post or deploy on retry, critical accessibility regression, workflow determinism breakage;
- no client's production data is held before the offsite backup copy and a recorded restore drill exist;
- nothing tenant-generated is served under the control-plane domain;
- development agents reach staging only; the production release is the operator's own action;
- the first live tenant is operator-owned.

## In scope
- End-to-end suite on staging with fake platforms, covering:
  1. request → site created → preview → client approval → deploy → health → rollback;
  2. draft → claim check → image → client approval → scheduled post → published once → proof of work → report;
  3. hours change → fact → site change → correction pack → verified;
  4. takedown of a published post and of a site page.
- Negative variants, each must fail closed: publish without client approval where policy requires it; edit after approval; deploy another tenant's artifact; post to another tenant's account; scheduled post after disconnect; double post on timeout; downtime across a post time; missing budget; paused tenant; tenant host trying to read a console cookie; preview without access; build escaping its sandbox; direct connector call outside the broker; injected instructions in a client's old site, a listing page and a client request.
- Real-platform checks on the operator's own test accounts: one Facebook Page post, one Instagram post, one LinkedIn company post, each with takedown; recorded.
- Disposition of every R3-tagged edge case: E-013, E-015 to E-023, E-054, E-075 to E-077, E-083, E-085, E-091.
- Readiness checklist, each item with evidence:
  - the tenant-site and preview domains are chosen, registered and separate from the control-plane domain;
  - OpenBao holds every production credential; none is in files or environment dumps;
  - the offsite backup target is in use (replacing the interim USB copy) and a restore drill from it is recorded;
  - the deletion ledger is re-applied in the restore drill;
  - Meta and LinkedIn app approvals are in place, or the limitation is written down;
  - privacy policy, data-deletion page and client-facing terms of the service exist and are linked where platforms require;
  - security-incident and content-takedown runbooks have been walked through once;
  - the operator's Google account has two-step verification with a passkey or hardware key; lost-phone procedure tried once;
  - starting budgets and limits are set for the first tenants; alerts fire at 80%;
  - an external reachability check and outage notice to the operator work;
  - the operator-handover note exists (who can do what if the operator is unavailable).
- Pilot: run the operator's own company tenant and the personal tenant live for a set period, with every side effect approved by hand. Record defects and cost.
- Go decision record for the first client tenant, signed by the operator.
- R3 exit report.

## Out of scope
- R4 capabilities.
- Uptime promises to clients. None are made from a single home host until measured.
- Tenant export and offboarding as a product workflow: no contract owns it yet. The runbook is the interim procedure; see open decisions.

## API / contract changes
None. Confirms every contract sketch added in R3 validates and matches the implementation.

## Data / migration
None. Confirms the full migration chain applies from empty and reverses, and the RLS coverage check reports no unprotected tenant table.

## Security / privacy threat notes
This task is the regression barrier for R3 threats: public mistakes under a client's name, token theft, tenant-site attacks on the console, sandbox escape, and loss of client data. The suite runs under the runtime database role and is a protected path.

## Edge cases covered
All R3-tagged entries listed above, each with a disposition: covered by test, covered by design, or deferred with a release and a note. E-017 (property transfer) and E-020 (long-lived connections) are deferred by design; E-015 (path sharing) is refused by design.

## Observability
The exit report links one full trace per positive journey and the audit trail of each negative variant. Dashboards exist for: actions by state, held and missed posts, connection health, certificate expiry, budget use, backup freshness.

## Acceptance criteria
- all positive journeys pass on a clean staging environment;
- every negative variant fails closed with an audit record naming the reason;
- every readiness item has evidence, or an explicit written waiver by the operator with a date;
- the restore drill from the offsite copy succeeded and its duration is recorded;
- the pilot ran for the agreed period with no release-blocker defect open;
- the monthly cost of a typical client's plan (content, posts, scans, reports) is measured and inside the client cap;
- the operator has signed the go decision.

## Tests
The suite itself, plus:
- mutation check on main guards: removing the client-approval check, the hash binding, the destination-tenant check or the reconcile-before-retry step makes at least one exit test fail;
- protected-path check for the suite;
- accessibility: automated results and a recorded manual pass on the client approval and preview journeys.

## Rollback / failure recovery
A failed exit keeps client work closed. Each failure becomes a defect on the owning task. During the pilot, the emergency hold (R3-008) and connector disable switches are the stop controls.

## Cost/resource budget
The suite runs on fakes. Real-platform checks and the pilot use the operator-owned caps (USD 30 per operator-owned company per month).

## Documentation updates
- R3 exit report under `evidence/`.
- `docs/PROJECT_REAUDIT_2026-08-10.md` dispositions; `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`; `00_START_HERE.md` status.
- First draft of the R4 task list.

## Open decisions
- **Decision required (owner, blocking):** the offsite backup target (Backblaze B2 is the leading candidate) and the tenant-site domains. Both are already listed as open.
- **Decision required (owner):** recovery objectives to state to clients (how much data may be lost, how long a restore may take). Proposed default: state none in writing until the first restore drills give measured numbers.
- **Decision required (owner):** pilot length before the first client. Proposed default: 30 days on the operator's own tenants.
- **Decision required (owner):** tenant export and offboarding. Edge cases E-058, E-059, E-082 and E-086 are tagged "R1+" and no R0 to R3 contract builds the export. Proposed default: add one contract, "Tenant export and offboarding workflow", to R3 before the first client is onboarded; until then the offboarding runbook is done by hand.
- **Decision required:** an external security test before the first client. Proposed default: yes, a scoped test of the console, the tenant-site boundary and the connect flows.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent review of the exit evidence; the operator's signed go decision is stored with the report.
