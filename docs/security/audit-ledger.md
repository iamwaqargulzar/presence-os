# Audit Ledger

Audit is append-oriented and human-readable.

Record:
- actor/user/service;
- tenant/profile;
- authority source;
- managed-operator context;
- action/task/workflow;
- request and artifact references;
- target/destination;
- policy decisions;
- connection used;
- model/harness where material;
- time;
- result;
- rollback/revocation;
- break-glass reason;
- relevant trace IDs.

Sensitive values are redacted or referenced, not dumped.

Audit records must help answer:
“Who or what did what, under whose authority, to which tenant, using which artifact, and what happened?”
