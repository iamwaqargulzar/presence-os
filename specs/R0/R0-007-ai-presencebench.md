# R0-007 — AI Capability, Execution Profiles and PresenceBench Skeleton

> **Spec revision:** 3 — 2026-11-14. Amended by [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md); the "ADR-0030 amendments" section overrides any conflicting text below it. Revision 2 (2026-11-10): Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement, including the 2026-08-10 qualification update, is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## ADR-0030 amendments (revision 3)
**Added to scope**
- Harness Registry entry: Claude Code driven through the Claude Agent SDK, status CANDIDATE until qualified on real tasks. Whether it replaces Prime Agent as primary worker is a separate decision; the revision 1 entries stay.
- Model Registry entry for a low-cost API model (intended: DeepSeek; exact model and price are data and must be revalidated).
- ExecutionProfile carries a **credential class**: `OPERATOR_SUBSCRIPTION` or `API`. A profile of class `OPERATOR_SUBSCRIPTION` may be resolved only for a run the operator started or approved.
- **Task-class routing** as registry configuration: planning, architecture, security-sensitive work and review map to a frontier profile; high-volume, low-risk, machine-checkable work maps to the low-cost profile.
- Default routing mode is CLOUD_ONLY. LOCAL_FIRST and LOCAL_ONLY remain declared but are not selectable while the inference host is off.

**Added acceptance criteria**
- a scheduled or unattended run cannot resolve an `OPERATOR_SUBSCRIPTION` profile (fails closed);
- changing the task-class mapping is a data change with no code change;
- the PresenceBench seed task is run once on the frontier profile and once on the low-cost profile, with success and cost recorded for both.

**Added tests**
- Credential-class gate: unattended run requesting a subscription profile is denied.
- Routing: each task class resolves to its configured profile; an unmapped class fails closed.

**Open decisions added**
- **Decided (ADR-0033):** (owner, 2026-11-15) DeepSeek V4.1 Flash for now, as configuration; a new tenant's low-cost profile receives only the `public` data class.

## Goal
Create provider-neutral capability interfaces and development-agent qualification metadata.

## Why now
Models, providers and harnesses are replaceable by constitution. If the first module calls a vendor SDK directly, that rule is already broken. R0-011 and R1-012 both build on these registries.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-061, E-062, E-066 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [AI Capability Gateway](../../docs/ai/capability-gateway.md)
- [Model, harness, controller and execution profile registry](../../docs/ai/model-harness-registry.md)
- [PresenceBench](../../docs/ai/presencebench.md)
- [Tenant AI model entitlements](../../docs/ai/tenant-ai-model-entitlements.md)
- [Prime baseline](../../benchmarks/presencebench/PRIME_BASELINE_2026-08-08.yaml), [harness telemetry evidence](../../evidence/HARNESS_TELEMETRY_AND_FLASH_BENCHMARK_2026-08-08.md)
- Contract: [execution-profile.schema.json](../../contracts/schemas/execution-profile.schema.json)
- ADR-0010, ADR-0012, ADR-0013, ADR-0025, ADR-0029

## Depends on
- R0-001, R0-002, R0-006 *(derived from build-plan lane 3)*.

## Invariants
- no application module imports a vendor SDK directly except the adapter layer;
- no harness, model or controller is embedded in product business logic;
- local inference is an optimisation and privacy option, never a hard dependency;
- production tenant AI credentials are separate from development harness subscription/OAuth credentials (ADR-0029);
- unavailable usage values are recorded as unavailable, never as zero;
- provider prompt-cache usage is never merged with local harness caches.

## In scope
- AI Capability Gateway interface with the representative operations (reason, generate_text, code, image, video, embed, rerank, vision, stt, tts, realtime_voice). Only a fake/test adapter and, at most, one real adapter are implemented.
- Routing-mode enumeration (LOCAL_FIRST, CLOUD_FIRST, CLOUD_ONLY, LOCAL_ONLY, SMART/AUTO) as a declared contract; routing logic may be minimal.
- Model Registry with capability metadata.
- Harness Registry with initial entries: Prime Agent (primary), Codex, Oh My Pi, OpenCode, ReasoniX.
- DevelopmentController registry, distinct from the Harness Registry, with the OpenHands-backed controller as CANARY/SELECTED.
- ExecutionProfile entity and lifecycle: DISCOVERED, CANDIDATE, QUALIFIED, SHADOW, CANARY, ACTIVE, RETIRED, REJECTED.
- HarnessAdapter and DevelopmentController interfaces as defined in the registry document (interfaces only; implementation is R0-011).
- Usage telemetry model with provenance grade (A provider exact, B persisted by harness, C harness calculation, D derived estimate, X unavailable).
- PresenceBench skeleton: evaluation identity record, one audited seed task, result recording for success/cost/cache/time.

## Out of scope
- Tenant AI identity, tenant provider policy and per-tenant model-profile resolution (R1-012).
- Context Compiler (R2).
- Private Inference/Voice Gateway on the GPU host.
- A new synthetic harness benchmark campaign.
- Secret holdout and red-team task sets (structure reserved, no content).

## API / contract changes
- Gateway interface and adapter plug-in contract.
- `execution-profile.schema.json` refined to match the implemented entity; any change is reviewed.
- Internal registry read interfaces consumed by R0-011 and R1-012.

## Data / migration
- Tables for model, harness, controller, execution profile and evaluation run records. These are platform-level, not tenant-scoped; state that explicitly and restrict writes to a platform role.
- Seed data for the initial harness and controller entries. Model names are data, not code.
- Reverse migrations tested.

## Security / privacy threat notes
- Provider credentials: referenced, never stored in registry rows or logged.
- Prompts and outputs in telemetry may contain tenant data: store references and usage numbers, not content, by default.
- Benchmark integrity: the seed task's verifier is not visible to or writable by the worker being evaluated.
- Model output is untrusted (`GENERATED` trust label) and never authorizes anything.

## Observability
- Every gateway call records operation, execution profile, provider/model, usage fields with provenance grade, latency and outcome, correlated with tenant/task where applicable.
- DevelopmentRun telemetry separately attributes controller, Prime parent, Prime child/reviewer and external build/tool resources.

## Acceptance criteria
- AI Capability Gateway interface;
- Model Registry;
- Harness Registry;
- ExecutionProfile entity/contract;
- adapters are pluggable;
- initial worker-harness entries: Prime Agent (primary), Codex, Oh My Pi, OpenCode, ReasoniX;
- DevelopmentController registry includes OpenHands-backed controller separately from worker harnesses;
- PresenceBench can run a tiny audited seed task and record success/cost/cache/time;
- no application module imports a vendor SDK directly except adapter layer;
- DevelopmentController registry is distinct from Harness Registry;
- initial controller implementation: OpenHands-backed, canary until real R0 telemetry validates overhead/reliability;
- primary worker harness: Prime Agent, based on the 2026-08-08 controlled Presence benchmark evidence;
- retain Codex/OpenCode/OMP/ReasoniX as replaceable fallback/challenger entries rather than active benchmark campaign;
- DevelopmentRun telemetry separately attributes controller, Prime parent, Prime child/reviewer and external build/tool resources;
- no further synthetic harness campaign is required before R0 implementation; real tasks feed PresenceBench.

## Tests
- Import-boundary test: a vendor SDK import outside the adapter layer fails a gate.
- Adapter swap: the same call succeeds against two adapters without caller changes.
- Capability check: a request needing a capability the profile lacks fails closed (E-006).
- Lifecycle: invalid ExecutionProfile transitions rejected.
- Seed task run recorded end to end with usage provenance grades.
- Unavailable usage is stored as unavailable.

## Rollback / failure recovery
Registries are data; a wrong entry is corrected by a new revision. If the one real adapter fails, the fake adapter keeps tests deterministic. No tenant-facing behaviour depends on this task yet.

## Cost/resource budget
The seed task must have a hard token/time limit and a recorded cost. Tests use the fake adapter and spend nothing.

## Documentation updates
- `docs/ai/capability-gateway.md`, `docs/ai/model-harness-registry.md`, `docs/ai/presencebench.md`.
- `benchmarks/presencebench/README.md` (how to run the seed task).
- `evals/README.md`.

## Open decisions
- **Decided (ADR-0033):** Anthropic first, then DeepSeek, behind the in-house gateway.
- **Decided (ADR-0033):** in the object store for 180 days; summary rows are kept without limit.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the seed run record is stored as evidence for R0-010.
