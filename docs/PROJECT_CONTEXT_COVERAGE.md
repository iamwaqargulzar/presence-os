# Project Context Coverage Map

This file exists to make loss obvious if the original planning chat is deleted.

| Planning area | Preserved in |
|---|---|
| Mission / truthful presence | product/vision-and-scope.md, CONSTITUTION.md |
| Business-first wedge | product/vision-and-scope.md, delivery/release-plan.md |
| Individual/company profiles | product/person-profile-tenant-model.md |
| Voice-first natural UX | product/conversation-and-home.md, ux/* |
| Agent visualizer / no face | product/conversation-and-home.md |
| Avoid AI-slop UI | ux/design-direction.md |
| Accessibility / WCAG | product/accessibility-localization.md |
| Multilingual / code switching / RTL | product/accessibility-localization.md |
| Attention / opportunities | product/attention-opportunities-and-scoring.md |
| Presence score / AI visibility stochasticity | product/attention-opportunities-and-scoring.md |
| Presence Graph / Passport | data/presence-graph-passport.md |
| Canonical truth / Candidate Facts / conflicts | data/knowledge-and-memory.md |
| Relationship graph / omnichannel | architecture/relationship-and-conversation-graph.md |
| Agent/skill/tool/provider abstraction | architecture/agent-skill-tool-model.md |
| Durable Temporal workflows | architecture/workflows-and-temporal.md |
| Context compiler / memory levels / cache | architecture/context-compiler.md, ai/context-cache-economics.md |
| Cost Governor | architecture/cost-resource-governance.md |
| Resource Governor / weighted priorities | architecture/cost-resource-governance.md |
| Human authority / direct request = approval | security/authority-and-action-broker.md |
| Outcome/artifact-bound approval | security/authority-and-action-broker.md |
| Managed-by-operator model and client roles | security/delegation-and-break-glass.md |
| Break glass | security/delegation-and-break-glass.md |
| Action state machine / idempotency | security/authority-and-action-broker.md, architecture/concurrency-idempotency.md |
| Prompt injection trust classes | security/trust-boundaries-and-prompt-injection.md |
| Fetch Broker / SSRF | security/fetch-broker.md |
| Upload quarantine | security/file-ingestion.md |
| OAuth/browser login/OTP approach | security/oauth-connections-browser.md |
| Postgres RLS | security/database-tenancy-rls.md |
| Secrets/OpenBao | security/secrets.md |
| Physical 3-server topology | infrastructure/topology.md |
| 4-VM lean Proxmox layout | infrastructure/topology.md |
| Inference private LAN | infrastructure/internal-networking-and-inference.md |
| RTX 3090 / 8700G / 32GB | infrastructure/topology.md, ai/local-inference-media-voice.md |
| Cloudflare Tunnel default | infrastructure/ingress.md |
| Future static-IP migration | infrastructure/ingress.md, runbooks/tunnel-to-static-origin.md |
| DMZ/direct-origin hardening | security/network-and-service-exposure.md |
| Random canonical hostname | domains/hostname-model.md |
| Vanity hostname plan/fee | domains/hostname-model.md, domains/vanity-policy.md |
| Separate control/tenant eTLD+1 | domains/domain-separation.md |
| Custom domain workflow | domains/custom-domains.md |
| Cloudflare wildcard/for-SaaS strategy | domains/cloudflare-strategy.md |
| Existing site preview/deploy/rollback | release + domain/runbook docs; R3 scope |
| Local/cloud AI gateway | ai/capability-gateway.md |
| Voice/STT/TTS candidates | ai/local-inference-media-voice.md |
| Image ComfyUI / video on demand | ai/local-inference-media-voice.md |
| Development factory | ai/development-factory.md |
| OpenHands controller / Prime worker / fallback harnesses | ai/model-harness-registry.md; ai/openhands-prime-development-factory.md |
| DeepSeek cache/cheap coding observation | ai/current-candidate-notes-2026-08.md |
| Thinking levels / progressive escalation | ai/development-cost-routing.md |
| PresenceBench / private holdouts | ai/presencebench.md |
| Public leaderboard only inspiration | ai/ai-coding-daily-reference.md |
| Code provenance / SLSA | ai/code-provenance-and-dependencies.md |
| R0–R5 plan | delivery/release-plan.md |
| Do-not-build-early list | delivery/do-not-build-early.md |
| Email deliverability / consent | integrations/email-outreach.md, data/consent-and-suppression.md |
| Social/Reddit/LinkedIn/browser constraints | integrations/social-browser-policy.md, product/capability-map.md |
| Career/job use case | product/capability-map.md |
| CRM/CRO/ecommerce/PR etc. envelope | product/capability-map.md |
| Tenant limits, budgets and usage | commercial/plans-entitlements-billing.md |
| Free Presence Scan / GTM | archived: archive/go-to-market.md (not current, ADR-0030) |
| Competitors/differentiation | archived: archive/competitive-position.md (not current, ADR-0030) |
| Offboarding/export/no lock-in | data/retention-export-offboarding.md, runbooks/tenant-offboarding.md |
| Platform Engineer / Ecosystem Watch | architecture/platform-engineer-and-ecosystem-watch.md |
| API maintenance agent concept | product/admin-and-managed-service.md |
| Backup/PBS/restore drills | infrastructure/backup-disaster-recovery.md, runbooks/backup-restore-drill.md |
| Admin Agent Home | product/admin-and-managed-service.md |

## 2026-08-10 additions
- OpenHands-backed DevelopmentController + Prime Agent worker/RPC integration;
- autonomous-development sandbox, supply-chain and token-overhead controls;
- multiple websites/custom applications per tenant via DigitalProperty;
- stable per-tenant Presence AI identity independent of model;
- task-class model routing, per-tenant override and provider policy, default change with rollback, run/session model pinning;
- operator-run model, client roles, Google-only sign-in, credential classes and in-house build preference (ADR-0030, ADR-0031);
- production AI credentials explicitly separated from development harness OAuth/subscriptions;
- expanded 60-item edge-case register.
