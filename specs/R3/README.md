# R3 — Business Presence

R3 is the first release used for real client work. Nothing is sold (ADR-0030). It adds the first real external side effects: building and hosting sites, publishing content, and posting to social platforms. Every one of them passes the Action Broker.

Do not implement until the R2 exit (R2-017) is accepted.

> **Status:** contracts written 2026-11-15, revision 1, before R1 and R2 are built. Each contract must be rechecked against the R1 and R2 implementation reports before its task starts. A change found then is a spec revision, not a silent edit.

## Task order

Tasks are listed in dependency order. A task may start when every task in its "Depends on" column is done.

| # | Task | Goal in one line | Depends on |
|---|---|---|---|
| 1 | [R3-001 Property Runtime Profiles and Build Pipeline](R3-001-runtime-profiles-build.md) | Build a property into a hashed release inside a sandbox, for a small qualified set of runtimes. | R2-017 |
| 2 | [R3-002 Tenant Site Serving, Preview and Custom Domain Go-Live](R3-002-serving-preview-domains.md) | Serve tenant sites and previews on their own domain, safely apart from the console. | R3-001 |
| 3 | [R3-003 Deploy, Health Check and Rollback](R3-003-deploy-health-rollback.md) | Put a verified release live through the Action Broker and undo it reliably. | R3-001, R3-002 |
| 4 | [R3-004 Website Create and Change](R3-004-website-create-change.md) | Create a site or change one from a plain request, always through a preview. | R3-003 |
| 5 | [R3-005 SEO, AEO and GEO Basics](R3-005-seo-aeo-geo-basics.md) | Make hosted sites readable and citable by search engines and AI engines. | R3-004 |
| 6 | [R3-006 Content Drafting and Brand Voice](R3-006-content-brand-voice.md) | Draft truthful text in the tenant's voice, with every claim traceable. | R2-017 |
| 7 | [R3-007 Image Generation through the Gateway](R3-007-image-generation.md) | Produce images through the AI Capability Gateway under budget and provider policy. | R3-006 |
| 8 | [R3-008 Publication Policy, Approval Execution and Takedown](R3-008-publication-approval-takedown.md) | One rule for when content may go public, and a fast way to take it back. | R3-006 |
| 9 | [R3-009 Social Publishing Core](R3-009-social-publishing-core.md) | Posts, calendar, connector contract and safe execution, with no platform code. | R3-008 |
| 10 | [R3-010 Meta Connector (Facebook Pages and Instagram)](R3-010-meta-connector.md) | The first real social connector. | R3-009 |
| 11 | [R3-011 LinkedIn Company Pages Connector](R3-011-linkedin-connector.md) | The second social connector. | R3-010 |
| 12 | [R3-012 Local Presence Basics](R3-012-local-presence-basics.md) | Keep name, address, phone and hours consistent, without a new connector. | R3-005, R3-006 |
| 13 | [R3-013 Progress Reporting and Proof of Work](R3-013-progress-proof-of-work.md) | Show the operator and the client what was done, with evidence and honest attribution. | R3-003, R3-009 |
| 14 | [R3-014 Client-Work Readiness and R3 Exit](R3-014-client-work-exit.md) | Prove R3 end to end and confirm the conditions for holding real client data. | all of the above |

## What may run in parallel

- The hosting lane (R3-001 to R3-005) beside the content and social lane (R3-006 to R3-011).
- R3-010 and R3-011 are done one after the other, never together (ADR-0031: one platform at a time).
- Only one task at a time may add migrations to the same module (E-029).

## Coverage of the release plan

| Capability named in the documents | Contract |
|---|---|
| qualified runtime profiles, multiple properties per tenant | R3-001 |
| preview, custom domains live | R3-002 |
| deploy, health, rollback | R3-003 |
| website create/change | R3-004 |
| SEO/AEO/GEO basics | R3-005 |
| content basics | R3-006 |
| image generation through the AI Capability Gateway | R3-007 |
| approvals/actions | R3-008 |
| social basics, in-house connectors | R3-009, then R3-010 (Meta), R3-011 (LinkedIn) |
| local basics | R3-012 |
| reporting/progress, Proof of Work | R3-013 |
| first release used for real client work | R3-014 |

## Not in R3

- CRM, email and outreach, lead discovery, messaging channels, voice receptionist (R4).
- Comments, direct messages and engagement on social platforms (R4).
- Managed browser profiles (R4, E-056).
- Paid advertising, ecommerce, video generation (R5).
- Social platforms other than Meta and LinkedIn. Each later platform is its own contract.
- Property transfer between tenants (E-017) and path sharing between properties (E-015).
- Arbitrary-language hosting. Only qualified runtime profiles are offered.
