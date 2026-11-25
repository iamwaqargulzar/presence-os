# PresenceBench

PresenceBench is the private evaluation system for models, harnesses, reasoning modes and context strategies used to develop and later operate Presence OS.

## Why

Public leaderboards are useful candidate-discovery signals, not production qualification.

PresenceBench tests the actual workload:
- Django
- Next.js/TypeScript
- PostgreSQL/RLS
- delegation/authority
- Temporal
- APIs/connectors
- accessibility
- security
- refactoring
- debugging
- migrations
- browser/E2E
- tool use
- long context
- recovery
- code review
- prompt injection
- cost/cache behavior.

## Evaluation identity

Record:
- model/provider/version
- harness/version
- reasoning config
- system prompt
- context strategy
- tools
- task/eval version
- trial
- environment.

## Sets

- Development
- Private Qualification
- Secret Holdout
- Historical Production Bugs
- Security Red-Team

Do not expose secret holdout to worker agents.

## Benchmark integrity

Public benchmark contamination/broken tasks are a known risk. Every important task must audit:
- spec/prompt;
- fixtures;
- hidden verifier;
- expected behavior;
- unintended shortcuts.

## Metrics

Quality:
- acceptance tests
- hidden tests
- regression rate
- security failures
- reviewer defects

Economics:
- total task cost
- cost/success
- cache savings
- repair/review/escalation cost

Efficiency:
- time
- turns
- tool calls
- tokens
- compactions

Autonomy:
- recovery
- stall
- premature-success rate
- human intervention.

## Qualification lifecycle

DISCOVERED → CANDIDATE → QUICK BENCH → FULL PRESENCEBENCH → QUALIFIED → SHADOW → CANARY → ACTIVE

Use champion/challenger per role.

Requalify after meaningful model, harness, prompt, tool or benchmark changes.

Use multiple trials for stochastic critical evaluations.

## Hard security gates

Zero tolerated for sensitive autonomous roles:
- cross-tenant escape
- secret leak
- destructive unauthorized action
- privilege escalation
- migration corruption.
