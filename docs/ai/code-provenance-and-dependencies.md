# Code Provenance and Dependency Policy

## Provenance

Track:
- task/spec hash;
- agent/model/harness/reasoning;
- starting commit;
- produced diff;
- tests/review;
- build artifact;
- deployment;
- final commit.

Adopt SLSA-style provenance progressively.

## Dependencies

Agent-added dependencies receive explicit review:
- license;
- maintenance health;
- vulnerabilities;
- source/reputation;
- release cadence;
- transitive weight;
- duplicate functionality;
- necessity.

Prefer standard library/existing dependencies where practical.

Do not let an agent add infrastructure (Kafka/Kubernetes/graph DB/etc.) merely because it is familiar.
