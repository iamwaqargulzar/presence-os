# Presence OS — Architecture Re-audit and Edge-Case Register

> **First written:** 2026-08-10. **Updated:** 2026-11-14 for ADR-0030 and ADR-0031.
>
> This is the project's edge-case register. It assumes that:
> 1. one tenant may own multiple hosted websites/custom applications;
> 2. each tenant experiences one logically singular Presence AI with a configurable model profile;
> 3. Presence OS is run by one operator for their own companies and managed clients, and is not sold (ADR-0030);
> 4. OpenHands is the initial development control-plane candidate, with Prime Agent and Claude Code (Agent SDK) as worker harnesses;
> 5. development must remain harness/model/controller replaceable.

## Executive conclusion

The prior architecture remains sound. No fundamental stack rewrite is required. The most important additions are control-plane clarifications rather than new infrastructure products:

- introduce **DigitalProperty** as a first-class tenant-owned resource so a tenant can host many sites/apps safely;
- separate the customer's stable **Presence AI identity** from the mutable model/provider profile underneath it;
- add **task class → Model Profile** policy with platform default, tenant override, run/session pinning, and default change with preview and rollback;
- explicitly separate **production tenant AI runtime** from **development-agent subscription/OAuth credentials**;
- use **OpenHands as development infrastructure/control plane** and **Prime Agent as the primary worker**, integrated through a versioned Prime RPC/process adapter rather than assuming native ACP;
- make ordinary development orchestration deterministic and token-free; spend LLM tokens only on reasoning work;
- add explicit autonomous-development sandbox, supply-chain, log-redaction, runaway-agent, stale-session, test-cheating, and parallel-migration controls;
- add property-level runtime, quota, domain, deployment, secret, and data ownership rules.

## Priority improvements

### P0 — before autonomous implementation is trusted

1. **Autonomous agents never receive production credentials.** Prime Agent is not a security sandbox; OpenHands headless operation can auto-approve actions. Run development agents only in dedicated isolated worker environments.
2. **Controller/worker separation.** OpenHands schedules and supervises; Prime solves coding tasks. Do not duplicate planning/reasoning by default.
3. **Prime RPC adapter contract.** Pin Prime version, handshake capabilities, correlate run/session IDs, recover orphaned sessions, stream events, normalize usage, and terminate process groups safely.
4. **Task/spec immutability.** Each development run records spec hash + start commit. Workers may not silently edit authoritative task contracts to make implementation easier.
5. **Protected verification.** Implementation agents cannot rewrite hidden/security acceptance tests. Sensitive tasks require independent review.
6. **No host Docker-socket trust shortcut.** Agent infrastructure must not expose a privileged Docker socket to untrusted agent code. Use dedicated worker host / restricted sandbox control path.
7. **Supervisor token accounting.** OpenHands-controller LLM usage, if any, is measured separately from Prime worker usage. Deterministic scheduling should require zero LLM calls.

### P1 — Presence Kernel additions

1. DigitalProperty + PropertyEnvironment + Deployment + HostnameAttachment.
2. Stable TenantAIIdentity + AIModelProfile + TenantAIConfiguration + tenant provider policy.
3. Model-profile resolution and run/session pinning.
4. Default model change with preview, exclusion list, rollback and audit.
5. Property limits/quotas separated from AI limits/quotas.
6. Fallback constrained by privacy, jurisdiction, capability, provider policy, credential class, budget and current authorization.

## Edge-case register

| ID | Area | Edge case / failure | Required control | Release |
|---|---|---|---|---|
| E-001 | Tenant AI | Admin changes default model mid-conversation | Pin effective AIModelProfile revision for each run/session; new policy applies at safe boundary | R1 |
| E-002 | Tenant AI | Tenant limit or budget lowered while an expensive workflow is waiting | Revalidate the limit before each expensive/side-effect stage; checkpoint and pause if no longer allowed | R1 |
| E-003 | Tenant AI | Model deprecated/outage | Capability-compatible fallback only if tenant policy permits; otherwise pause with actionable status | R1/R2 |
| E-004 | Tenant AI | Tenant override names a profile its provider policy or budget does not allow | Override is validated at set time and at resolution; invalid override is rejected with a reason | R1 |
| E-005 | Tenant AI | Default model change overwrites pinned clients | Preview the affected set; pinned and policy-excluded tenants are never changed; rollback | R1 |
| E-006 | Tenant AI | Model has no required tool/vision/structured-output feature | Capability registry blocks selection before run | R0/R1 |
| E-007 | Tenant AI | Fallback violates local-only/privacy policy | Privacy/data-residency constraints are hard filters, not ranking preferences | R1 |
| E-008 | Tenant AI | Raw token counts are not comparable across models | Budgets are in money from an actual-cost ledger with price snapshots; raw tokens are kept for observability | R1 |
| E-009 | Tenant AI | Quota exhausted mid-task | Reserve budget, checkpoint, stop before uncontrolled overage, tell the operator | R1/R2 |
| E-010 | Tenant AI | Client expects one AI but router changes model invisibly | Stable Presence AI identity; admin-visible effective profile; optional PINNED routing mode | R1/R2 |
| E-011 | Tenant AI | Model switch loses “memory” | Memory/knowledge live in Presence stores, never in model-local state as canonical source | R2 |
| E-012 | Tenant AI | Platform Admin AI reads tenant data by default | Separate platform authority; explicit TenantAccessGrant/break-glass only | R1 |
| E-013 | Multi-property | Tenant owns 20 sites/apps | DigitalProperty is first-class; tenant limits and resource governor bound count/concurrency | R1/R3 |
| E-014 | Multi-property | Two properties claim same hostname | Atomic unique hostname registry; ownership verification; canonical attachment | R1 |
| E-015 | Multi-property | Site and app share a domain/path | No arbitrary path-sharing initially; require explicit gateway route model before supporting | R3+ |
| E-016 | Multi-property | Property deleted while domain still points at platform | Tombstone + safe holding response; detach after retention window; prevent hostname takeover | R1/R3 |
| E-017 | Multi-property | Property transfer between tenants | Explicit transfer workflow rebinds ownership, secrets, domain verification, audit and billing; never update tenant_id ad hoc | R3+ |
| E-018 | Multi-property | App needs DB migrations while another deployment runs | Per-property migration lane/lock; forward/backward-compatible deploy pattern | R3 |
| E-019 | Multi-property | Background jobs survive rollback | Deployment revision owns worker/cron revision; rollback reconciles jobs | R3/R4 |
| E-020 | Multi-property | WebSocket/long-lived connections during deploy | Drain/reconnect strategy; version-aware routing | R3+ |
| E-021 | Multi-property | One app consumes all CPU/build slots | Per-tenant + per-property resource quotas and weighted fair queues | R1/R3 |
| E-022 | Multi-property | Secret reused accidentally across apps | Secrets namespace includes tenant + property + environment; shared secrets must be explicitly linked | R1/R3 |
| E-023 | Multi-property | Preview leaks private app | Authenticated preview + noindex + random preview ID + expiry | R1/R3 |
| E-024 | Development | OpenHands repeatedly “thinks” while Prime already works | Deterministic supervisor mode; LLM supervisor only on anomaly/escalation with explicit budget | R0 |
| E-025 | Development | Prime subagent tree explodes | Max child count/depth/token/time per task; total-tree accounting | R0 |
| E-026 | Development | Prime daemon survives cancelled run | Controller terminates process group/session and verifies no retained child/schedule/heartbeat remains | R0 |
| E-027 | Development | Network disconnect creates duplicate worker | Run lease + idempotent run ID + single active lease per task/worktree | R0 |
| E-028 | Development | Two agents edit same files | File/area ownership hints + isolated worktrees + integration gate; serialize high-conflict tasks | R0 |
| E-029 | Development | Parallel schema migrations conflict | Dedicated migration lane; only one migration-producing task per bounded schema area at a time | R0 |
| E-030 | Development | Agent changes tests to make itself pass | Protected baseline/hidden tests; diff policy; independent evaluator | R0 |
| E-031 | Development | Agent modifies task/spec to reduce acceptance | Task contract/spec hash immutable for worker; change requires separate spec-revision task | R0 |
| E-032 | Development | Harness auto-refines itself and benchmark becomes irreproducible | Disable/lock Prime refinement for qualified production profiles; review/version refinements separately | R0 |
| E-033 | Development | OpenHands/Prime update changes behavior | Pin versions; canary on real low-risk task; preserve previous version and rollback | R0 |
| E-034 | Development | Agent installs malicious dependency | lockfiles, dependency policy, secret scan, vulnerability/license checks, SBOM/provenance | R0 |
| E-035 | Development | Repo/web content prompt-injects coding agent | Treat repository/external content as untrusted unless designated control files; limited network/tools | R0 |
| E-036 | Development | Session JSONL/log contains credential | redaction scanner before persistence/export; secrets never placed in prompts/logs when avoidable | R0 |
| E-037 | Development | Agent can reach Proxmox/LAN from worker | deny-by-default egress; no management subnet; no production/service credentials | R0 |
| E-038 | Development | Docker socket gives root-equivalent host control | do not expose unrestricted host Docker socket to agent-controlled process; isolate runtime manager | R0 |
| E-039 | Development | “Tests passed” is fabricated | Controller runs gates independently from Prime and records exit codes/artifacts | R0 |
| E-040 | Development | Long autonomous run burns subscription/API quota | task resource reservation + max turns/tokens/time + live usage circuit breaker + checkpoint | R0 |
| E-041 | Development | Supervisor overhead erases Prime cache advantage | separate usage IDs/cost ledgers; alert/stop when supervisor exceeds configured overhead budget | R0 |
| E-042 | Development | OpenHands unavailable | Prime-only adapter path remains supported; source of truth remains Git/specs | R0 |
| E-043 | Data | vector query misses tenant filter | tenant/RLS enforced below retrieval layer; negative cross-tenant tests | R1/R2 |
| E-044 | Data | shared prompt/result cache leaks tenant content | tenant/profile/property + policy revision included in cache key; sensitive caches encrypted/short-lived | R0/R1 |
| E-045 | Data | deleted data remains in embeddings/cache/backups | deletion ledger + cache invalidation + vector deletion + retention/backup policy; legal-hold exception explicit | R1/R2 |
| E-046 | Data | contradictory company facts | CandidateFact/conflict pipeline; no auto-canonical overwrite | R2 |
| E-047 | Actions | queued action executes after auth/connection revoked | delayed revalidation immediately before side effect | R1 |
| E-048 | Actions | approved content changes after approval | artifact hash binding invalidates authorization on material change | R1 |
| E-049 | Actions | provider times out after successful side effect | provider/request idempotency + uncertain-outcome state; never claim generic exactly-once | R1 |
| E-050 | Actions | webhook replay creates duplicate work/action | signature + timestamp window + event idempotency key | R1/R4 |
| E-051 | Scheduling | DST/timezone changes shift posts | store timezone + local scheduling intent + resolved execution instant; recalculate future recurrence safely | R2/R3 |
| E-052 | Budgets | operator pauses a tenant while workflows are active | tenant operating state; block new work; complete or abort reserved actions according to the recorded policy | R1 |
| E-053 | Budgets | model price changes after reservation | price/version snapshot at reservation; settle actual; policy revision affects new reservations | R1 |
| E-054 | Domain | custom domain expires/reassigned | periodic ownership/DNS health; suspend sensitive serving if ownership evidence fails | R1/R3 |
| E-055 | Domain | vanity hostname recycled too early | quarantine/tombstone; do not immediately recycle high-use names | R1 |
| E-056 | Browser | browser identity crosses tenants | browser profile namespace tenant+connection; hard isolation and lifecycle cleanup | R1/R4 |
| E-057 | Files | zip bomb / parser exploit | quarantine, size/decompression limits, sandbox parser/CDR | R1 |
| E-058 | Offboarding | tenant export omits AI memory/properties | Passport/export includes knowledge, memories, properties, domains, artifacts, connections metadata and audit where exportable | R1+ |
| E-059 | Offboarding | legal hold conflicts with deletion request | explicit retention/legal-hold state; restrict access while preserving only required data | R1+ |
| E-060 | Admin | bulk platform change becomes tenant side effect | platform config changes use a separate admin action class, preview and audit; never mint tenant business authority | R1 |
| E-061 | AI credentials | scheduled, unattended or client-triggered run tries to use the operator's subscription | credential class on every profile; resolver denies `OPERATOR_SUBSCRIPTION` unless the operator started or approved the run | R0/R1 |
| E-062 | Inference | GPU host is powered off and a run needs a local-only profile | cloud-only default; local modes not offered while the host is off; such a run pauses with a reason | R0/R1 |
| E-063 | Privacy | low-cost provider receives a data class the client did not allow | tenant provider policy is a hard filter in resolution and fallback, for every task class | R1 |
| E-064 | Budgets | one client's activity exhausts the global budget and stops every other client | tenant budget checked first; global budget alert threshold below its cap | R1 |
| E-065 | AI | subscription rate limit reached in the middle of a run | run ends BUDGET_EXHAUSTED with the reason; resume later or reroute to an API profile if policy allows | R0 |
| E-066 | AI | provider changes how subscription or Agent SDK usage is billed or permitted | adapter treats billing as usage data; moving a task class to an API profile is a configuration change; terms rechecked before reliance | R0 |
| E-067 | Identity | an uninvited Google account completes Google sign-in | refused after authentication; no user, session or tenant-visible record is created | R0 |
| E-068 | Identity | an email address is reassigned to a different Google account | identity bound to Google's stable subject identifier, not the email string | R0 |
| E-069 | Identity | operator's Google account is locked, or Google is unavailable | documented recovery with no password back door; running workflows are unaffected | R0 |
| E-070 | Identity | operator's Google account is taken over | two-step verification required; session list and revoke; high-risk actions keep consequence-specific confirmation; Cloudflare Access in front of the console is an open decision | R0 |
| E-071 | Clients | a client request starts AI work or an external action | no client role holds `start_ai_work`; a request only creates a queue item | R1 |
| E-072 | Clients | a client approves a draft that was changed afterwards | approval is artifact-bound to the exact content hash; a changed draft needs a new approval | R1 |
| E-073 | Clients | invitation revoked while the client has open sessions | revocation ends sessions and takes effect on the next request | R0 |
| E-074 | Clients | client connects the wrong or a personal account | show the connected account's identity for confirmation before the first post; client can disconnect | R1 |
| E-075 | Connections | a platform withdraws the developer app's approval or API access | connector health state; hold queued posts; attention item for the operator; connector API-change runbook | R3 |
| E-076 | Connections | token refresh fails overnight before scheduled posts | posts are held, not dropped; reauthentication request to the client; health checked at execution time | R1/R3 |
| E-077 | Social | retry after an unknown result publishes a post twice | idempotency key per post; reconcile with the platform before any retry (see E-049) | R3 |
| E-078 | Scheduling | a scheduled task needs the frontier profile but nobody is present | prepare the work and notify the operator, or use an API profile; never fall through to the subscription | R2 |
| E-079 | Scheduling | operator is away and approvals pile up | pending approvals expire; nothing auto-approves; one digest instead of many alerts | R2 |
| E-080 | Domains | DNS record left pointing at a deleted property (takeover risk) | hostname attachment and DNS removed in the delete workflow; periodic dangling-record scan | R1 |
| E-081 | Workflows | a deploy changes workflow code while workflows are in flight | workflow versioning and replay tests before deploy | R0 |
| E-082 | Privacy | erasure request while the data still exists in backups | stated backup expiry window; a deletion ledger is re-applied after any restore | R1+ |
| E-083 | Content | generated content infringes copyright or a trademark, or defames | publication requires approval; provenance recorded; fast takedown path | R3 |
| E-084 | Infrastructure | the whole site is lost (fire, theft, long power loss) | encrypted offsite backup, documented rebuild, stated recovery objectives | R0 |
| E-085 | Infrastructure | home internet or power outage takes client sites offline | UPS and clean shutdown; outage visible to the operator; whether static sites are also served from an edge cache is an open decision | R0/R3 |
| E-086 | Operations | the single operator is unavailable for a long time | written handover procedure; each client can receive an export of their own data and properties | R1+ |
| E-087 | Dev worker | prompt injection makes the worker reveal its own subscription login | login outside the workspace, path restrictions, egress allow list, redaction scan | R0 |
| E-088 | Provenance | code copied from a reference project brings its licence into Presence OS | build-in-house rule: study only, copy nothing; provenance review in the gate policy | R0 |
| E-089 | AI | the low-cost provider is unavailable | fallback only within the tenant's provider policy; otherwise the work is queued | R1 |
| E-090 | Identity | operator's phone is lost or stolen | revoke Presence sessions; sign the device out of the Google account; documented and tried once | R0 |
| E-091 | Scheduling | the system was down at the time a post or task was scheduled | on restart, missed items are detected and held for the operator with a stated lateness window; nothing is published late without a decision and nothing is silently dropped | R3 |
| E-092 | Scheduling | a scheduled run is treated as pre-approved and skips the Action Broker | schedules only start runs; every side effect passes the same authority, limit and approval checks as a manual run; negative test | R2 |
| E-093 | Identity | a stolen console session is used to run commands on the Worker VM | session alone is not enough for high-risk actions; step-up confirmation; worker accepts only signed controller requests, never browser requests | R0 |
| E-094 | Supply chain | an imported skill or prompt pack contains hostile instructions or code | packs are reviewed, pinned by hash and treated as dependencies; no marketplace auto-install; pack text is never control authority | R2 |

## Architectural improvements deliberately *not* added now

The audit does **not** justify Kubernetes, Kafka, a graph database, a separate vector database, per-tenant VMs, or a complex service mesh. OpenHands/Prime also do not justify giving development agents production access. The existing lean Proxmox + modular monolith + Postgres/Temporal/Redis design remains the preferred initial shape.

## New source-of-truth documents

- `docs/product/digital-properties-and-hosting.md`
- `docs/ai/tenant-ai-model-entitlements.md`
- `docs/ai/openhands-prime-development-factory.md`
- `docs/ai/prime-worker-adapter.md`
- `docs/security/autonomous-development-security.md`
- `docs/operations/model-policy-change-management.md`
- ADR-0021 through ADR-0033
- R0-011/R0-012 and R1-011/R1-012/R1-013 task contracts
