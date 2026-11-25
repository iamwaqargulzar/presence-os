# Context, Cache and AI Economics

## Principle

The cost of an agentic task depends on far more than headline output-token price.

Track:
- uncached input tokens;
- cache reads;
- cache writes;
- output/reasoning tokens;
- number of turns;
- tool calls;
- compactions;
- retries;
- review/repair;
- wall time;
- external tool/media cost.

## Stable prompt prefix

Place stable instructions/contracts before dynamic state.

Do not continuously rewrite cache-stable policy/AGENTS/tool contracts merely to store progress.

Durable task/spec artifacts reduce repeated architect reasoning.

## Structured artifact reuse

Research, snapshots, competitor analysis and media outputs should be stored as reusable structured artifacts.

Tool-result cache freshness is data-type-specific.

## Cost metric

Primary development/runtime metric:
**total expected cost per successful task/outcome**, not price per token.

A more expensive model may be cheaper if it avoids many failures; a cheap model may dominate when harness/cache behavior keeps success high.

## Controller overhead
For OpenHands + Prime development, keep separate ledgers for controller LLM usage, Prime parent, Prime children/reviewers and external build/tool compute. Deterministic scheduling should consume zero model tokens. Alert/circuit-break when controller/supervisor AI overhead exceeds its configured per-run budget rather than allowing silent duplicate reasoning.
