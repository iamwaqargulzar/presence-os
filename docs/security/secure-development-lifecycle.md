# Secure Development Lifecycle

Security is a gate, not a final audit.

## Baseline practices

- threat model new privileged capabilities;
- static analysis;
- dependency scanning;
- secret scanning;
- SAST/DAST where useful;
- migration tests;
- RLS/authorization tests;
- tenant-boundary tests;
- fuzz/negative tests for parsers and brokers;
- prompt-injection/red-team tests for agent workflows;
- provenance for autonomous changes;
- code review independent of implementation agent for sensitive work.

Use OWASP ASVS as a verification baseline and OWASP guidance for LLM prompt injection/insecure output handling.

## Zero tolerance in autonomous qualification

An execution profile fails sensitive autonomy qualification if it demonstrates:
- cross-tenant escape;
- secret leak;
- unauthorized external action;
- privilege escalation;
- destructive production behavior;
- migration corruption without safe recovery.

## Autonomous controller/worker boundary
OpenHands/Prime agents run without production credentials or management-network reachability. Prime is controlled through a versioned adapter, and worker “completion” is independently verified. Protected tests/spec hashes, dependency policy, log redaction, agent-tree limits and orphan cleanup are mandatory before sustained autonomy.
