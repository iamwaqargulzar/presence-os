# Privacy and Data Governance


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


This is an engineering baseline, not jurisdiction-specific legal advice. Before public launch, map actual processing to applicable privacy/marketing/consumer laws with qualified counsel.

## Data minimization

Collect/store only what is needed for:
- identity/presence;
- requested services;
- security/audit;
- billing;
- legal obligations.

Do not use “AI might need it someday” as a retention basis.

## Data classes

At minimum:
- PUBLIC
- TENANT_INTERNAL
- CONFIDENTIAL
- SECRET/CREDENTIAL
- REGULATED/SENSITIVE where applicable

Class drives:
- model/provider eligibility;
- logging;
- storage;
- encryption;
- retention;
- export;
- deletion.

## AI processing

Tenant/provider policy can restrict:
- cloud processing;
- specific providers;
- data classes;
- geography/residency later.

Record enough provenance to answer which provider/model processed a material artifact without logging unnecessary sensitive prompts.

## Data subject/customer controls

Design for:
- access/export;
- correction;
- deletion/retention exceptions;
- consent evidence;
- connection revocation;
- tenant offboarding.

## Cross-tenant analytics

Use aggregated/de-identified metrics where practical. Do not make one tenant's private business data retrievable in another tenant's model context.
