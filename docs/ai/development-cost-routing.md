# Development Cost Routing

## Progressive escalation

Do not automatically start routine coding at maximum reasoning.

Example policy:
1. trivial/mechanical profile;
2. default cheap implementation profile;
3. higher reasoning on failure/complexity;
4. alternate cheap profile;
5. senior reviewer/implementer;
6. frontier architect only when justified.

## Expected cost to completion

Router should consider:
- cost spent so far;
- probability next profile succeeds;
- historical task-class success;
- retry cost;
- review cost;
- elapsed time;
- risk class.

Do not run five more cheap failures when one qualified senior attempt has lower expected completion cost.

## Cache metrics

Track:
- cache_hit_ratio
- cache_read_tokens
- cache_write_tokens
- uncached_input_tokens
- stable_prefix retention
- context invalidations
- compaction count
- effective cost.

Harness overhead should be benchmarked separately on trivial deterministic tasks.

## Native vs controlled tracks

PresenceBench should have:
- **Controlled Track:** comparable tools/context to isolate model behavior.
- **Native Production Track:** each model uses its best-qualified harness/context strategy.

Production routing cares most about the second.

## Development controller routing
Controller is not a reason to add another frontier model call. Prefer deterministic policy. If controller reasoning is required, choose a separately budgeted execution profile and include it in total cost-to-completion.
