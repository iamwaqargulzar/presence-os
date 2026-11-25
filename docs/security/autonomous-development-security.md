# Autonomous Development Security Boundary

> Authoritative addition — 2026-08-10.

## Threat assumption

Model-generated shell/Python/code, repository content, dependency scripts, web content, MCP output and agent extensions may be malicious or simply wrong. Development agents are privileged automation, not trusted human engineers.

Prime Agent's own documentation states its worker/kernel lifecycle is **not a security sandbox** and commands execute with the current user's permissions. OpenHands headless mode is documented as always-approve. Therefore the surrounding environment provides the security boundary.

## Required isolation

Run autonomous development only on a dedicated Worker VM/host or equivalent isolation tier with:
- no Proxmox management access;
- no production database/Redis/Temporal/object-store credentials;
- no Cloudflare/DNS production credentials;
- no tenant OAuth/social/email credentials;
- no platform billing credentials;
- no SSH keys that can reach production;
- deny-by-default management-network access;
- sandboxed code execution (gVisor/container/VM profile as appropriate);
- disposable worktree/build/test resources.

## Docker control-plane warning

A raw Docker socket is effectively a host-control capability. Do not expose an unrestricted host Docker socket to an agent-controlled process/container. If OpenHands Agent Server needs container lifecycle, run it on the dedicated worker host and keep the agent workspace separated from the runtime-manager privilege, or use a narrowly scoped broker/remote sandbox design.

## Network egress

Default development worker policy:
- allow source/dependency registries required for the task through controlled egress;
- block private LAN, metadata endpoints, Proxmox, inference-management ports and production control-plane addresses;
- web research is off unless task policy enables it;
- external content remains untrusted data.

## Supply-chain controls

Agent may not silently broaden dependency trust. Require:
- lockfile changes visible in diff;
- package-source policy;
- secret scan;
- vulnerability/dependency scan;
- license policy where relevant;
- SBOM/provenance generation by release stage;
- review for install scripts/native binaries/high-risk dependencies.

## Spec/test integrity

Worker cannot write protected hidden/security tests or authoritative task/spec controls for the run. Test fixtures and public tests may be modified only when the task explicitly allows it; controller compares protected baseline.

## Session/log hygiene

Prime/OpenHands session events may contain prompts, paths, command output and accidental secrets. Before long-term persistence or sharing:
- redact credential/token/cookie patterns;
- remove home/user-specific paths where not required;
- encrypt sensitive logs at rest;
- apply retention policy;
- never upload/share raw traces by default.

## Autonomous limits

Every run has hard limits for:
- wall time;
- model calls/turns;
- input/output/compute budget;
- tool calls where appropriate;
- root/child agent count;
- child depth;
- retries;
- build/runtime resources.

Hitting a limit means `BUDGET_EXHAUSTED`/`TIMED_OUT`, not success.

## Production boundary

Development agents may produce merge candidates and staging artifacts. They do not receive standing authority to deploy to production. Production promotion remains Release Controller/human-authorized initially, with canary/rollback later.
