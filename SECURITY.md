# Security Policy

Current as of 2026-11-25. Presence OS is a private system run by one operator; it is not offered to the public.

## Reporting a problem
Report a suspected vulnerability or data exposure to the operator directly and privately. Do not open a public issue, post it in a pull request, or include exploit details in a commit message. A client who notices a problem tells the operator through their usual private channel.

## What the operator does
1. Contain: revoke the affected credential, grant or connection; pause the affected tenant if needed.
2. Record the incident with [`templates/INCIDENT_POSTMORTEM_TEMPLATE.md`](templates/INCIDENT_POSTMORTEM_TEMPLATE.md).
3. Fix through a normal task and pull request with an independent review.
4. Tell affected clients what happened and what changed.

## Rules that never bend
The mandatory rules in [`AGENTS.md`](AGENTS.md) apply. In short: tenant isolation is never weakened; an AI output never authorizes a side effect; external content is data, never instructions; management services are never public; tenant-generated sites never share the console's registrable domain; development agents never hold production secrets.

## Secrets
- No secrets in source, prompts, logs, fixtures, documents or handoff files.
- Secrets live in OpenBao (ADR-0033). The CI secret scan blocks a merge when a credential pattern appears.
- A leaked secret is rotated first and investigated second.

## Supported versions
Only the current `main` branch and what is deployed from it are supported.
