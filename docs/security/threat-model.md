# Threat Model

Presence OS combines multi-tenancy, autonomous agents, untrusted web content, browsers, external credentials, generated code and public sites. Treat compromise paths explicitly.

## Assets
- tenant canonical knowledge;
- customer content/assets;
- OAuth/API credentials;
- domains/DNS;
- budgets and usage ledger;
- production infrastructure;
- audit/provenance;
- customer communications/reputation.

## Threat actors
- unauthenticated Internet attacker;
- malicious/compromised tenant user;
- cross-tenant attacker;
- compromised external website/email/file;
- malicious dependency;
- compromised provider account;
- buggy/misled autonomous agent;
- compromised worker/browser sandbox;
- internal privileged user.

## High-risk threats and controls

### Cross-tenant data access
Controls: tenant_id, Postgres RLS, runtime-role design, object/file scoping, security tests.

### Prompt injection / indirect instruction
Controls: trust labels, least tools, deterministic authority, Action Broker, Fetch Broker, output validation.

### Unauthorized external action
Controls: AuthorizationGrant, artifact/target binding, risk confirmation, revalidation, idempotency, audit.

### SSRF/private network discovery
Controls: Fetch Broker scheme/DNS/redirect/private-range checks and worker egress restrictions.

### Secret theft
Controls: OpenBao/Secrets Broker, no model/log exposure, short-lived credentials, sandbox isolation.

### Generated-code escape
Controls: gVisor, no Docker socket, restricted mounts/egress, no management/GPU/private network access.

### Browser-account takeover
Controls: tenant-scoped browser identities, user-entered credentials/OTP, health/challenge states, no CAPTCHA bypass, least access.

### Domain takeover/misrouting
Controls: ownership verification, state machine, audited DNS actions, canonical fallback, certificate monitoring.

### Duplicate destructive side effect
Controls: idempotency, Action state machine, revalidation, optimistic concurrency.

### Supply-chain compromise
Controls: dependency policy, scanning, provenance, pinned lockfiles, review.

### Noisy-neighbor/DoS
Controls: Resource Governor, weighted fair queues, rate limits, quotas, circuit breakers.

### Backup compromise
Controls: separate backup target, encrypted offsite copy, protected credentials, restore drills.
