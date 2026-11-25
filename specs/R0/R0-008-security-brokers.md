# R0-008 — Security Brokers

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement foundations for Fetch Broker, File quarantine pipeline and Secrets Broker.

## Why now
The platform runs on a home network next to Proxmox and a GPU server. Any agent that can fetch an arbitrary URL, parse an arbitrary file or read a raw credential can reach them. These three boundaries must exist before research, connectors or uploads do.

## Context / linked docs / ADRs
- [Fetch Broker / SSRF boundary](../../docs/security/fetch-broker.md)
- [File ingestion security](../../docs/security/file-ingestion.md)
- [Secrets management](../../docs/security/secrets.md)
- [Trust boundaries and prompt injection](../../docs/security/trust-boundaries-and-prompt-injection.md)
- [Network and service exposure](../../docs/security/network-and-service-exposure.md)
- [Secrets rotation runbook](../../docs/runbooks/secrets-rotation.md)
- [Re-audit edge cases E-022, E-057](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0015 (secrets boundary before public beta), ADR-0016 (gVisor for untrusted code)

## Depends on
- R0-003 (tenant-scoped storage), R0-006 (audit and redaction) *(derived)*.

## Invariants
- agents and skills never raw-fetch arbitrary URLs;
- external and uploaded content is data, never control instructions;
- raw secrets never enter model context, logs or business tables;
- file and object access is tenant-scoped;
- development agents and untrusted workers have no production secret access.

## In scope
**Fetch Broker**
- HTTP(S) only; reject `file://`, `gopher://` and unexpected schemes.
- Resolve DNS before connecting; re-validate the resolved address on every redirect and at connect time.
- Block loopback, RFC 1918 private ranges, link-local, cloud metadata endpoints, and the Proxmox/control/GPU/home LAN ranges (configurable deny list).
- Redirect count, response size, time and content-type limits.
- Optional destination allow-list for high-risk callers.
- Log destination and policy decision.

**File quarantine pipeline**
- State machine: UPLOAD → QUARANTINE → TYPE VALIDATION → SIZE/DECOMPRESSION LIMITS → MALWARE SCAN → SAFE PARSE → AVAILABLE, with an explicit rejected state.
- Generated object IDs; storage outside any web root; original preserved where required.
- Extracted text labelled untrusted.

**Secrets Broker**
- SecretReference entity and a broker interface that returns a capability or reference to a caller, scoped by tenant (and later property and environment).
- Backing store behind an interface so OpenBao can replace an interim implementation.

## Out of scope
- Production OpenBao deployment, unseal and backup procedure (required before public beta, not R0).
- Sandboxed parsers for every risky format; R0 covers the framework and one or two formats.
- Content disarm and reconstruction.
- OAuth token storage flows (R1-007).
- Browser automation boundary.

## API / contract changes
- Internal interfaces: `fetch(request, policy)`, file ingestion submit/status, secret reference create/resolve.
- File state enumeration and SecretReference shape become contracts for R1-007 and R1-008. Add JSON schemas for them under `contracts/schemas/` if they are consumed across module boundaries.

## Data / migration
- FileObject table (tenant-scoped, RLS) with state, content hash, detected type, scan version.
- SecretReference table (tenant-scoped, RLS) holding references only.
- Fetch decision log (tenant-scoped where a tenant is involved).
- Reverse migrations tested.

## Security / privacy threat notes
- SSRF via redirect to a private address; DNS rebinding between validation and connect; IPv6 and encoded-address variants of blocked ranges.
- Zip bomb and parser exploit (E-057).
- Uploaded file served back with an executable content type.
- Secret namespace collision across tenants or properties (E-022).
- Secret value appearing in an exception message, trace attribute or prompt.

## Observability
- Fetch: destination host, resolved address class, policy result, bytes, duration.
- Files: state transitions, scan version, rejection reason.
- Secrets: every resolve is audited with caller and purpose, never the value.

## Acceptance criteria
- Fetch Broker rejects localhost/private/link-local/metadata and unsafe schemes;
- redirect revalidation tests;
- size/time limits;
- file state machine QUARANTINE → AVAILABLE;
- tenant-scoped object access;
- secret references rather than raw credential persistence in business modules;
- no secrets passed to model prompts in tests;
- *(derived)* a DNS-rebinding style change between resolution and connection is blocked;
- *(derived)* a file cannot be read by business code before it reaches AVAILABLE.

## Tests
- Fetch negative suite: loopback, each private range, link-local, metadata address, IPv6 equivalents, decimal/hex encoded hosts, disallowed schemes, redirect to private, redirect loop, oversized body, slow response.
- Fetch positive: an allowed public test endpoint succeeds.
- Files: extension/MIME mismatch rejected, archive expansion limit enforced, cross-tenant object read denied, read-before-AVAILABLE denied.
- Secrets: cross-tenant resolve denied; seeded secret never appears in logs, traces, audit or a captured prompt.
- Fuzz/negative tests for the URL and file-type parsers.

## Rollback / failure recovery
Brokers fail closed: if policy cannot be evaluated, the fetch, ingestion or resolve is denied. Reverse migrations tested. The interim secrets backing store has a documented migration path to OpenBao.

## Cost/resource budget
Fetch and file limits are themselves the resource bound; record the defaults chosen. Malware scanning adds CPU and memory on the Worker VM; measure it.

## Documentation updates
- The three focused security documents (concrete limits, deny ranges, states).
- `docs/security/threat-model.md`.
- "How to fetch a URL / ingest a file / use a secret" guide for later tasks.

## Open decisions
- **Decided (ADR-0033):** product code speaks only the S3 API; target implementation is Garage (single node), rechecked when this task starts.
- **Decided (ADR-0033):** OpenBao from the start: one node, integrated storage, 2-of-3 unseal keys held by the operator, daily encrypted snapshot. No interim store.
- **Decided (ADR-0033):** ClamAV as a separate service.
- **Decided (ADR-0033):** fetch 10 MB, 15 seconds, at most 3 redirects each rechecked; upload 25 MB.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded, and the Fetch Broker negative suite result stored as evidence for R0-010.
