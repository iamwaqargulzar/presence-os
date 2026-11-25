# Coding-Harness Telemetry and DeepSeek V4 Flash Benchmark — Full Handoff Report

**Report date:** 2026-08-08 (Asia/Karachi)  
**Status:** Preliminary; one trial per selected Flash harness  
**Audience:** A receiving agent or technical reviewer continuing this evaluation  
**Safety:** This report is sanitized. It contains authentication modes only, never credential values, account identifiers, cookies, or tokens.

## 1. Executive summary

Five installed coding-agent CLIs were audited locally for authentication modes, token and cache telemetry, persistence, machine-readable extraction, cost semantics, and subscription behavior:

1. Codex CLI 0.147.0
2. OpenCode 1.18.15
3. Oh My Pi 17.2.11
4. Prime Agent 0.7.1
5. ReasoniX 1.21.2

After the no-cost audit, an authorized unscored Prime Agent pilot and four controlled DeepSeek V4 Flash attempts were run. No GPT-5.6, Sol, Terra, Luna, or native-model track was invoked.

Prime Agent was the only harness to complete the entire frozen single-agent benchmark successfully. Its final test suite passed 61/61, its fresh-session architecture review found all 20 seeded defects, and it received an independent score of 89/100.

That result does **not** establish that Prime Agent is the only useful harness. The experiment was designed to prohibit subagents:

- ReasoniX produced substantial correct work and passed 92 independent Phase 1 tests, but its native metrics disclosed worker/subagent activity. It was disqualified for violating the single-agent protocol even though it may be well suited to an orchestrator-plus-workers workflow.
- Oh My Pi was interrupted by a fault in the operator's telemetry reducer. This was not a clean failure of the harness or model.
- OpenCode ended early after setup and produced insufficient evidence in its single attempt.
- Prime Agent's successful run had subagents disabled, so the run proves single-agent execution and telemetry—not multi-agent orchestration.

The defensible conclusion is therefore:

> Prime Agent is the only harness validated by this one controlled single-agent trial. ReasoniX is the only tested harness that visibly exercised worker agents, but its orchestration quality and efficiency were not evaluated under an orchestration-appropriate protocol.

All conclusions remain preliminary because there was only one attempt per harness and three of the four scored profiles did not yield eligible, comparable completions.

## 2. Scope and safety constraints

The work followed these restrictions:

- Local inspection was read-only during the telemetry audit.
- Authentication and configuration were not changed.
- No harness was installed, upgraded, or downgraded.
- Existing sessions were not altered.
- No inference was used merely to discover schemas.
- The only inference calls were the explicitly authorized Prime pilot and DeepSeek V4 Flash benchmark attempts.
- No credentials, account identifiers, subscription tokens, or sensitive home paths were retained in report artifacts.
- No repeat trials were made after an invalid or incomplete run.
- No GPT-5.6 models were invoked.

The benchmark archive was verified before execution:

- Archive SHA-256: `9a14060e3f35f1c8e0e37001efcdad186a7b01c2b1647e0a35b680645ebad9b5`
- Internal manifest entries checked: 155
- Manifest mismatches: 0

The checksum describes the original frozen archive. The extracted tree was subsequently extended with authorized telemetry, workspaces, and reports.

## 3. Reliability and metric terminology

Every metric source uses the requested reliability classification:

| Grade | Meaning |
|---|---|
| A | Provider-originated exact usage at receipt |
| B | Provider usage persisted by the harness |
| C | Harness or tokenizer estimate/calculation |
| D | Derived or otherwise approximate |
| X | Unavailable |

Three monetary concepts must remain separate:

- **Actual cost:** an explicitly observed provider-billed amount.
- **API-equivalent cost:** a harness calculation using catalog/API token prices.
- **Subscription capacity:** a quota or allowance reduction, which is not necessarily a dollar charge.

In this study, no harness exposed a verified actual billed dollar amount for the Flash attempts.

### Prompt-cache interpretation

`cache read`, `cached input`, or `cache hit` refers to provider prompt-cache accounting unless stated otherwise. It is not the harness's local file cache, session database cache, or unique conversation size.

Cached prefixes are counted on every model request. If a 100,000-token prefix is reused in 20 calls, accounting can show approximately two million cache-read tokens even though the conversation does not contain two million unique tokens.

Reasoning tokens, when separately exposed, are generally a subset of output tokens and must not be added to the total a second time.

## 4. Installed-harness telemetry audit

| Harness | Current authentication mode | Best machine-readable source | Token/cache reliability | Cost semantics | Subscription/quota |
|---|---|---|---|---|---|
| Codex CLI 0.147.0 | ChatGPT subscription/OAuth | Rollout JSONL | B persisted provider usage | Actual dollar cost unavailable | Provider rate-limit/quota state available |
| OpenCode 1.18.15 | OpenCode Go API credential plus OpenAI OAuth | SQLite, corroborated by run JSONL | B | Catalog/API-equivalent calculation | No stable native quota source found |
| Oh My Pi 17.2.11 | OpenCode Go API credential plus OpenAI Codex OAuth | Session JSONL plus redacted quota snapshot | B; context partly C | Catalog/API-equivalent calculation | Redacted provider capacity available |
| Prime Agent 0.7.1 | OpenCode Go API credential plus OpenAI Codex OAuth | Session JSONL plus JSON/RPC output | B; context partly C | Catalog/API-equivalent calculation | No stable native quota source found |
| ReasoniX 1.21.2 | OpenCode Go API credential | Metrics JSON plus events JSONL and trajectory | B where populated | Zero/empty-currency result was semantically unavailable | No stable native quota source found |

### Codex CLI 0.147.0

Supported authentication includes ChatGPT subscription/OAuth and API-key/BYOK. The currently configured mode is ChatGPT subscription/OAuth.

Useful native interfaces:

- `codex login status`
- interactive `/status`
- interactive `/usage`
- `codex exec --json ...` for JSONL events when an authorized model call is made

Persisted rollout JSONL provides input, cached input, cache-write input, output, reasoning output, total tokens, context-window metadata, model, reasoning effort, rate limits, and structured tool-call events. Provider usage is A at receipt and B after persistence. Dollar cost is X for subscription sessions. Displayed context percentage and a computed cache miss are derived.

Codex was audited but was not part of the authorized DeepSeek V4 Flash scored sequence because its prepared tracks targeted later GPT-5.6 testing.

### OpenCode 1.18.15

Supported modes include API/BYOK credentials and provider OAuth. The current setup includes OpenCode Go API authentication and OpenAI OAuth. The Flash route used OpenCode Go.

Useful native interfaces:

- `opencode auth list`
- `opencode stats`
- `opencode session list --format json`
- `opencode export --sanitize <session-id>`
- `opencode db path`
- `opencode db --format json <SQL>`
- `opencode run --format json ...` when a model call is authorized

The SQLite message/session records persist input, output, reasoning, cache read, cache write, total, model/variant, cost, and tool parts. Token/cache fields are B. Cost is a C/D API-equivalent calculation, not verified subscription spend. Cache miss is not native and would be D if derived.

### Oh My Pi 17.2.11

Supported modes include subscription/OAuth and API/BYOK. The current setup includes OpenAI Codex OAuth and an OpenCode Go credential. Flash used OpenCode Go.

Useful native interfaces:

- `omp stats --json`
- `omp usage --json --redact`
- interactive `/usage`, `/stats`, `/context`, and `/session`
- `omp --mode json ...`
- `omp --mode rpc ...`

Session JSONL contains input, output, cache read, cache write, total, context tokens, optional reasoning tokens, calculated cost, model/provider, reasoning level, tool calls, and orchestration metadata. The Flash attempt confirmed separate reasoning-token population. Context is partly tokenizer-estimated. Redacted quota snapshots are available and must be stored separately from calculated cost.

### Prime Agent 0.7.1

Supported modes include subscription/OAuth and API/BYOK. The current setup includes OpenAI Codex OAuth and an OpenCode Go credential. Both pilot and benchmark used OpenCode Go.

Useful native interfaces:

- interactive `/usage`, `/context`, and `/session`
- `prime-agent --mode json ...`
- `prime-agent --mode rpc ...`
- `prime-agent --resume <session>`

Session JSONL contains provider/model, thinking level, input, output, cache read, cache write, total tokens, calculated cost, and structured tool calls. Token/cache fields are B. This version has no separate reasoning-token field. Context display is partly estimated. JSON delta output repeatedly includes growing message state and can grow quadratically; online collectors should retain terminal events and session JSONL rather than every repeated snapshot.

### ReasoniX 1.21.2

ReasoniX supports configured provider credentials. The current mode is OpenCode Go API authentication; the model was routed explicitly through `opencode-go/deepseek-v4-flash`.

Useful native interfaces:

- `reasonix run --events-jsonl <path>`
- `reasonix run --metrics <path>`
- `reasonix run --trajectory <path>`
- `reasonix run --resume <session>`
- `reasonix run --model <provider/model> --effort high`
- `reasonix run --ablate subagent,retrieval`

The Flash attempt populated prompt, completion, cache-hit, cache-miss, calls by source, tool calls, failures, steps, and compactions. Cache-write and reasoning-token totals were unavailable. The metrics file is essential because it revealed subagent calls that were not obvious in the sanitized events. Its cost field was zero with an empty currency, so cost is treated as unavailable—not as proof of a free run.

## 5. Prime Agent calibration pilot

Before the scored runs, Prime Agent completed a separate two-turn, unscored pilot with `opencode-go/deepseek-v4-flash`, high reasoning, and `RLM_MAX_DEPTH=0`.

The pilot created and tested a small Python ledger, then resumed the same session to add reservation release behavior. It passed every gate:

- Exact provider/model on all 18 model calls
- High reasoning setting persisted
- Same-session continuation for Turn 2
- No fallback, subagent, web, memory, or refinement activity
- Files confined to the pilot workspace
- Final independent test result: 25 passed
- Both turns separately attributable
- Model identity, calls, tool calls, elapsed time, and native token/cache fields recovered
- Sanitization scan passed

This pilot proved the Prime route and collector before the scored sequence began.

## 6. Controlled DeepSeek V4 Flash benchmark

### Frozen protocol

The selected harnesses ran in this order:

1. ReasoniX
2. Prime Agent
3. Oh My Pi
4. OpenCode

Each profile requested the exact model `opencode-go/deepseek-v4-flash` with high reasoning, a pristine isolated workspace, frozen prompts, no operator steering, and no fallback, web research, memory mutation, refinement, or auxiliary model activity. The protocol prohibited subagents. Coding Phase 1, Phase 2, and Context Continuation were to share a session; Architecture Review was to use a fresh session.

### Outcome summary

| Harness | Classification | Correctness evidence | Main qualification issue | Wall time | Model/tool calls | API-equivalent cost |
|---|---|---|---|---:|---:|---:|
| ReasoniX | DISQUALIFIED | 92 independent Phase 1 tests passed | Native metrics disclosed prohibited subagent activity; no resumable session; final-readiness exit 1 | 37.01 min | 190 / 192 | Unavailable |
| Prime Agent | PRELIMINARY PASS | 61/61 final tests; architecture 20/20 | Only eligible successful run; single trial | 23.97 min | 82 / 80 | $0.0355703292 |
| Oh My Pi | DISQUALIFIED due instrumentation | 25 passed, 1 failed at interruption | Operator reducer crashed and caused EPIPE | 7.91 min | 22 / 32 | $0.0255386992 |
| OpenCode | INSUFFICIENT DATA | No source or tests produced | Ended after setup with unknown final step | 2.15 min | 4 / 4 | $0.0005997236 |

The dollar figures are catalog/API-equivalent calculations, not verified charges.

## 7. Exact token and cache accounting

| Harness/run | New/non-cached input | Cache read/hit | Cache miss | Cache write | Output | Reasoning | Native total | Reliability notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Prime Agent complete | 27,895 | 7,123,328 | Unavailable | 0 | 168,893 | Unavailable separately | 7,320,116 | Token/cache B; cost C/D |
| ReasoniX Phase 1 | 11,859,648 prompt total | 10,701,568 | 1,158,080 | Unavailable | 243,906 | Unavailable | 12,103,554 | Prompt/cache/output B; miss conservatively D |
| Oh My Pi partial | 34,040 | 1,121,664 | Unavailable | 0 | 62,973 | 40,690 | 1,218,677 | Token/cache/reasoning B; partial invalid run |
| OpenCode partial | 7,285 | 13,824 | Unavailable | 0 | 435 | 68 | 21,612 | Token/cache/reasoning B; insufficient run |

For ReasoniX, the 10,701,568 cache-hit tokens are included inside 11,859,648 prompt tokens. The 1,158,080 cache-miss value corresponds to their difference and is retained with conservative derived provenance. For Prime, OMP, and OpenCode, cache-read is represented as a component alongside newly processed input in the normalized totals.

OMP and OpenCode totals must not be compared economically against Prime's total: those runs stopped during Phase 1, while Prime completed all coding phases plus a fresh architecture review. ReasoniX also performed a different effective workload because worker activity and 12 compactions occurred before it stopped.

### Prime phase-by-phase accounting

| Phase | Tests | Model calls | Tool calls | Input | Cache read | Cache write | Output | Seconds | API-equivalent cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Phase 1 | 34 passed | 36 | 37 | 10,436 | 2,118,144 | 0 | 76,454 | 607.70 | $0.0143994816 |
| Phase 2 | 52 passed | 27 | 26 | 3,328 | 3,010,688 | 0 | 39,695 | 388.01 | $0.0100052232 |
| Context Continuation | 61 passed | 14 | 13 | 1,894 | 1,892,864 | 0 | 14,626 | 141.41 | $0.0048302296 |
| Architecture Review | n/a | 5 | 4 | 12,237 | 101,632 | 0 | 38,118 | 300.82 | $0.0063353948 |
| **Total** | **61 final** | **82** | **80** | **27,895** | **7,123,328** | **0** | **168,893** | **1,437.94** | **$0.0355703292** |

## 8. Per-harness run findings

### ReasoniX

ReasoniX ran for approximately 37 minutes. Its independent Phase 1 suite collected and passed 92 tests. Native metrics recorded:

- 190 model calls
- 192 tool calls, including 17 failures
- 14 subagent model calls
- 20 subagent tool calls
- 12 compactions

It had been launched with `--ablate subagent,retrieval`, yet worker activity remained visible in `usage_by_source`. Under the frozen single-agent rules this was a hard disqualification. The command also returned a final-readiness failure with incomplete TODOs and did not produce a usable resumable session, so subsequent phases were not started.

Interpretation for future work: this is evidence that ReasoniX can activate workers, not evidence that its orchestration is good or bad. The present benchmark intentionally treated any delegation as invalid and did not score delegation quality, worker specialization, integration, or token efficiency.

### Prime Agent

Prime was restricted to a single exact model, high reasoning, `RLM_MAX_DEPTH=0`, isolated sessions, and no external skills, templates, context files, web, fallback, memory mutation, or refinement. No prohibited activity was observed.

It completed the required same-session coding sequence and the fresh-session architecture review. Independent validation found:

- Final suite: 61/61 passed
- Architecture review: 20/20 seeded defects found
- Evaluator score: 89/100
- Correct implementation of authorization revalidation, persistent SQLite state, concurrent duplicate handling, request-bound idempotency, budget reservation/settlement, explicit uncertain-outcome behavior, and correlation-preserving audit queries

Residual production risks:

- External connector I/O occurs while holding a SQLite write transaction, limiting concurrency and leaving a post-side-effect/pre-commit crash window.
- Actual cost can exceed the reservation and overspend.
- Outcome-unknown rollback loses detailed attempt rows and preserves only a summary.
- Resource and artifact registries assume globally unique IDs instead of explicit tenant-qualified ownership.
- Denial audit persistence is best-effort if a follow-up storage transaction also fails.

This was a strong single-agent result. It does not validate Prime as an orchestrator because worker depth was deliberately disabled.

### Oh My Pi

OMP reached 25 passing tests with one failure still present when the operator's streaming telemetry reducer encountered a valid string-form message record. The reducer had assumed structured-list content, crashed, closed stdout, and caused OMP to record an EPIPE recovery state.

This is an operator instrumentation failure, not a clean harness failure. No retry or resume was attempted because the benchmark prohibited repeats and steering. The collector was subsequently corrected to accept both string and structured content, but that correction was not used to change the scored result.

OMP provided the best subscription-capacity observation in this set: its redacted OpenCode Go capacity delta was 0.025539, matching its $0.0255386992 catalog calculation to six decimals. This remains a capacity observation, not proof of an actual dollar charge.

### OpenCode

OpenCode used pure mode, a static title, the exact model and high variant, with task delegation, web access, external skills, user questions, and external-directory access disabled.

It made four model-step attempts and four tool calls, inspected the environment, created a TODO list and empty project directory, then ended with exit code 0 but an `unknown` final step. It created no implementation and ran no tests. Because continuing would have required an additional operator prompt, the profile stopped as insufficient data.

One such outcome is not enough to conclude that OpenCode cannot complete the task. A clean repeat is required to test reproducibility.

## 9. Orchestrator-plus-workers interpretation

The original controlled benchmark answers: **Which harness can autonomously complete this task as one constrained agent?** It does not answer: **Which harness is the best orchestrator of multiple workers?**

For the user's intended architecture—a single harness hosting an orchestrator and worker agents—the current evidence means:

- **Prime Agent:** best validated executor, but orchestration untested.
- **ReasoniX:** demonstrated worker activation and complete-looking Phase 1 code, but orchestration was penalized instead of evaluated. Its high call count indicates potentially significant coordination overhead.
- **Oh My Pi:** orchestration not tested; completion remains unknown because instrumentation interrupted it.
- **OpenCode:** orchestration intentionally disabled; the incomplete attempt provides no useful orchestration evidence.
- **Codex CLI:** telemetry capability audited, but no DeepSeek Flash orchestration run was authorized.

A future orchestrator benchmark should allow delegation explicitly and normalize all usage across the entire agent tree. It should capture:

- Orchestrator tokens, cache reads/writes, model calls, and tool calls
- Per-worker tokens, cache reads/writes, model calls, and tool calls
- Worker role and delegated task
- Parallel versus sequential elapsed time
- Duplicate investigation or implementation work
- Failed delegations and retries
- Integration/review calls by the orchestrator
- Shared-context versus per-worker prompt-cache behavior
- Final independent correctness and architecture scores
- Total API-equivalent cost and separately observed subscription-capacity change

The core comparison should be useful verified work per total agent-tree token—not merely the main agent's usage. A harness that hides worker usage would be ineligible for a trustworthy efficiency comparison.

## 10. Recommended automated collector

Use one canonical record per run and phase containing:

- Run ID, harness/version, phase, sanitized session hash, timestamps, elapsed seconds
- Requested and observed provider/model/reasoning
- Input, cache read, cache write, native cache miss, derived cache miss, output, reasoning, and total tokens
- Model calls, tool calls by name, compactions, context resets, and subagent source
- Actual cost, API-equivalent cost, and subscription-capacity delta as separate nullable fields
- Source artifact and source field path for every metric
- Provenance grade A/B/C/D/X for every value
- Validity flags for fallback, delegation, web, memory, refinement, wrong model, sequencing, and workspace escape

Harness adapters should use:

1. **Codex:** rollout JSONL token-count and response-item events.
2. **OpenCode:** read-only SQLite scoped to session/message IDs, cross-checked with run JSONL.
3. **OMP:** isolated session JSONL plus redacted before/after quota snapshots.
4. **Prime:** isolated session JSONL plus terminal JSON output and an external timer.
5. **ReasoniX:** metrics JSON merged with events JSONL and trajectory; always inspect `usage_by_source` for delegation.

Collector rules:

- Never replace unavailable values with zero.
- Deduplicate cumulative token snapshots.
- Derive phase deltas only between adjacent cumulative snapshots.
- Preserve native totals even when components do not reconcile.
- Count failed/fallback model attempts as calls.
- Keep provider prompt-cache metrics distinct from local harness caching.
- Hash session identifiers and redact home/user prefixes.
- Reject credential-shaped values before preserving or sharing artifacts.

## 11. What is known, unknown, and requires authorization

### Known without more inference

- Installed versions and configured authentication modes
- Local telemetry schemas and best extraction interfaces
- Native token/cache fields for the tested OpenCode Go Flash route
- Prime's complete single-agent result and phase-level usage
- ReasoniX's total and subagent activity for Phase 1
- OMP's partial usage and the reducer-induced interruption
- OpenCode's partial usage and premature end

### Unknown because account/billing interfaces are needed

- Actual billed cost for Prime, ReasoniX, OMP, and OpenCode
- Reliable Prime, ReasoniX, and OpenCode subscription-capacity attribution
- Whether ReasoniX's zero/empty-currency cost means unpriced, included, or unavailable

Another diagnostic prompt would not resolve these billing questions.

### Unknown because a new benchmark run is needed

- Whether OMP completes cleanly with the corrected collector
- Whether OpenCode's premature `unknown` termination is reproducible
- Whether ReasoniX can disable workers reliably when strict single-agent operation is desired
- Whether Prime can act as an effective orchestrator when worker depth is enabled
- Comparative orchestrator/worker correctness and total-tree token efficiency

No such repeat or orchestration run has been performed. New inference requires explicit authorization and a newly frozen protocol.

## 12. Recommended next decision

Do not choose a permanent orchestrator based solely on the current single-agent benchmark.

If multi-agent orchestration is the target, the smallest useful next experiment is a two-harness orchestration pilot:

1. Prime Agent with workers explicitly enabled and fully attributed.
2. ReasoniX with its native worker behavior explicitly permitted and fully attributed.

Use the same compact task, the same maximum worker count, the same model, the same reasoning level, isolated workspaces, and independent tests. Record both orchestrator-only and total-tree usage. Stop after one trial each and compare correctness first, then wall time, model calls, cache usage, and API-equivalent consumption.

OMP and OpenCode can be rerun separately to resolve their incomplete single-agent outcomes, but those reruns answer a different question from orchestrator selection.

## 13. Evidence index

All paths below are relative to the benchmark root and contain sanitized evidence only where intended for sharing:

- `operator/INTERIM_RESULTS_FLASH.md` — concise benchmark outcome
- `operator/RESULTS_COMPARISON.csv` — normalized comparison row per attempt
- `operator/PRIME_INDEPENDENT_EVALUATION.md` — detailed Prime evaluation
- `telemetry-audit/00_SUMMARY.md` — telemetry audit summary
- `telemetry-audit/metric-matrix.csv` — cross-harness metric availability and provenance
- `telemetry-audit/recommended-collector-design.md` — collector specification
- `telemetry-audit/{codex,opencode,oh-my-pi,prime-agent,reasonix}.md` — per-harness audit
- `telemetry-audit/calibration/prime-agent-flash/PILOT_RESULT.md` — pilot gate evidence
- `harnesses/*/deepseek-v4-flash/results/*.md` — per-run result reports
- `telemetry-audit/raw-command-notes/archive-verification.md` — archive integrity evidence

Large or detailed session artifacts should not be shared blindly. Any receiving agent should use the summarized reports first and independently sanitize raw telemetry again before moving it outside the local benchmark workspace.

## 14. Final conclusion

Token and prompt-cache consumption were successfully measured from native persisted telemetry. Prime Agent completed the full single-agent benchmark with 7,320,116 native token events, including 7,123,328 repeated cache-read tokens, and was the only eligible successful run. ReasoniX consumed 12,103,554 token events during Phase 1 and disclosed meaningful worker activity, but the protocol disqualified exactly that behavior.

Therefore, the current data supports Prime as the strongest validated **single-agent executor**, while leaving the **orchestrator** decision open. A deliberately multi-agent, total-tree-metered comparison between Prime and ReasoniX is the most direct next step, subject to explicit authorization.
