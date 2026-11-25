# R1-008 — Artifact and File Ownership/Versioning

> **Spec revision:** 2 — 2026-11-10. Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement tenant-scoped Artifact/File objects, content hash/version/base_version, quarantine integration and exact artifact reference required by artifact-bound approvals.

## Why now
An artifact-bound approval is meaningless unless "post v82" identifies immutable bytes. Workflows also need to pass references instead of payloads, and deployments (R1-011) need a hashed release artifact.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-072 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Concurrency, idempotency and consistency](../../docs/architecture/concurrency-idempotency.md)
- [Authority and Action Broker](../../docs/security/authority-and-action-broker.md) (artifact-bound mode)
- [File ingestion security](../../docs/security/file-ingestion.md)
- [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md)
- [Retention, export and offboarding](../../docs/data/retention-export-offboarding.md)
- [Re-audit edge cases E-045, E-048](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0018 (customer ownership)

## Depends on
- R0-003, R0-006, R0-008 (file quarantine pipeline, object storage access).
- Supplies the artifact check implementation for R1-003.

## Invariants
- an artifact version is immutable: new content is a new version with a new hash;
- a stale edit returns a conflict, never an overwrite;
- uploaded files are unusable until the quarantine pipeline marks them AVAILABLE;
- large content lives in object storage; rows and workflow history carry references;
- object access is tenant-scoped and uses generated IDs; object keys are never authorization;
- the customer owns and can export their artifacts.

## In scope
- Artifact entity (logical item) and ArtifactVersion (immutable content with hash, size, media type, author, created_at, origin: human, generated, imported).
- `version` / `base_version` optimistic concurrency on the artifact head.
- Content hash defined over canonical bytes with a named algorithm.
- Exact reference format: (artifact ID, version, hash) as used by AuthorizationGrant and Action.
- Verification interface for the Action Broker: does this reference still match?
- FileObject linkage to the R0-008 pipeline; an artifact version can be backed by a file only when it is AVAILABLE.
- Tenant-scoped storage access with short-lived, scoped download capability.
- Ownership scope fields allowing later attachment to a DigitalProperty.
- Soft-delete marker and a deletion-ledger entry hook (E-045).

## Out of scope
- Rich editors, diffing and merge.
- Derived data cleanup (embeddings, caches) beyond the ledger hook.
- Export packaging (Passport).
- Retention schedules.
- Media transformations.

## API / contract changes
- Internal: create artifact, add version(base_version), get, list versions, resolve reference, verify reference.
- Endpoints for upload initiation and download capability.
- New contract sketch `artifact.schema.json` (and artifact reference) since the reference crosses Authorization, Action Broker and property deployment boundaries.

## Data / migration
- Tables: Artifact, ArtifactVersion; FileObject from R0-008 linked. Tenant-scoped under RLS.
- ArtifactVersion rows are immutable at the database privilege level (no UPDATE of content fields by the runtime role).
- Object storage layout namespaced by tenant using generated IDs.
- Reverse migrations tested.

## Security / privacy threat notes
- Approved content replaced after approval (E-048).
- Cross-tenant read through a guessed object key or a leaked download capability.
- Hash computed over non-canonical representation, letting two "equal" artifacts differ.
- Quarantine bypass: an artifact version pointing at a file that never became AVAILABLE.
- Generated content treated as trusted: carry the GENERATED trust label.
- Deleted content surviving in derived stores (E-045).

## Observability
- Audit: artifact created, version added (with author and origin), reference verified/failed, download capability issued, soft delete.
- Metrics: version conflicts, verification failures, storage by tenant.

## Acceptance criteria
- *(revision 1)* tenant-scoped Artifact and File objects;
- *(revision 1)* content hash, version and base_version;
- *(revision 1)* quarantine integration;
- *(revision 1)* exact artifact reference usable by artifact-bound approvals;
- *(derived)* a version's content cannot be modified after creation;
- *(derived)* an artifact-bound grant minted for version N fails validation for version N+1;
- *(derived)* a download capability expires and is bound to one tenant and one object.

## Tests
- Concurrency: two writers with the same `base_version` → one conflict.
- Immutability: UPDATE of version content rejected under the runtime role.
- Hash: identical bytes give identical hash; one changed byte fails verification.
- Quarantine: version creation from a non-AVAILABLE file denied.
- Cross-tenant RLS suite; object fetch with another tenant's key denied; expired capability denied.
- End to end with R1-002/R1-003: approve version N, edit to N+1, execution refused.

## Rollback / failure recovery
An upload that fails after object write leaves an orphan object: a reconciliation job removes unreferenced objects. Reverse migrations tested. No hard deletion in this task, so a mistaken soft delete is reversible.

## Cost/resource budget
Storage grows with versions. Expose storage per tenant as a usage dimension for R1-004 and define a maximum object size.

## Documentation updates
- `docs/architecture/concurrency-idempotency.md` (hash algorithm, reference format).
- `contracts/README.md` and the new schema.
- Guide: "how to store and reference an artifact".

## Open decisions
- **Decided (ADR-0033):** SHA-256; structured content is canonicalised with RFC 8785 before hashing.
- **Decided (ADR-0033):** as R0-008: S3 API only, Garage as the target.
- **Decided (ADR-0033):** 2 GB; all versions are kept in R1.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the R1-003 artifact-check stub is replaced by this implementation.
