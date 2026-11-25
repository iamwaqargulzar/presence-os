# Change Management

All material changes are traceable to:
- task/spec;
- issue/incident/opportunity;
- code diff;
- tests/review;
- release.

## High-risk changes

Require stronger review:
- auth/authorization;
- RLS;
- secrets;
- limits and budgets;
- destructive actions;
- DNS/domains;
- connector permissions;
- migration touching tenant ownership;
- sandbox/network boundaries.

## Feature flags

Use controlled flags for risky or gradual behavior.

Do not leave permanent stale flags; give flags owner, purpose and cleanup condition.
