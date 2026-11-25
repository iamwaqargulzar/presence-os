# External Standards and Current Reference Registry


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-10** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


This registry records authoritative/current references used to shape the handoff. Revalidate time-sensitive vendor facts before implementation/purchase.

## Security / identity

- OAuth 2.0 Security Best Current Practice — RFC 9700 (Jan 2025)
  https://www.rfc-editor.org/rfc/rfc9700
- OAuth 2.0 for Browser-Based Applications — RFC 10017 (Jul 2026)
  https://www.rfc-editor.org/rfc/rfc10017
- OWASP Application Security Verification Standard (ASVS), current stable 5.0.0 at baseline
  https://owasp.org/www-project-application-security-verification-standard/
- OWASP Top 10 for LLM Applications / Prompt Injection
  https://owasp.org/www-project-top-10-for-large-language-model-applications/

## Accessibility

- W3C WCAG 2.2 Recommendation
  https://www.w3.org/TR/WCAG22/

## Cloudflare / domains

- Cloudflare Tunnel — outbound-only, no public IP required, all plans at baseline
  https://developers.cloudflare.com/tunnel/
- Cloudflare for SaaS
  https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/
- Cloudflare for SaaS plans — at baseline Free/Pro/Business list 100 included hostnames, up to 50,000, $0.10 additional
  https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/plans/
- Custom hostnames
  https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/domain-support/
- Universal SSL limitations — root + first-level subdomain in full setup; deeper names require additional certificate capability
  https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/limitations/

## Database

- PostgreSQL Row Security Policies
  https://www.postgresql.org/docs/current/ddl-rowsecurity.html

## Durable workflows

- Temporal documentation
  https://docs.temporal.io/
- Worker Versioning GA announcement (Mar 30 2026)
  https://temporal.io/changelog/worker-versioning-continue-as-new-worker-controller

## Secrets

- OpenBao
  https://openbao.org/
- OpenBao security model
  https://openbao.org/docs/internals/security/

## Sandboxing

- gVisor overview
  https://gvisor.dev/docs/
- gVisor production guidance
  https://gvisor.dev/docs/user_guide/production/

## Supply chain

- SLSA v1.2 Provenance
  https://slsa.dev/spec/v1.2/provenance

## Coding harnesses

- OpenAI Codex
  https://help.openai.com/en/collections/14937394-codex
- OpenCode models/variants
  https://opencode.ai/v2/docs/models
- OpenCode Go model economics (time-sensitive)
  https://opencode.ai/docs/go/
- DeepSeek ReasoniX integration — cache-first / Flash-first native design
  https://api-docs.deepseek.com/quick_start/agent_integrations/reasonix
- Pi documentation
  https://pi.dev/docs/latest
- Pi RPC
  https://pi.dev/docs/latest/rpc
- Pi SDK
  https://pi.dev/docs/latest/sdk

## Community benchmark inspiration

- AI Coding Daily leaderboard
  https://aicodingdaily.com/leaderboard

This leaderboard is not a Presence OS dependency and not a qualification authority.


## Direct-origin Cloudflare hardening

- Authenticated Origin Pulls (available on Free/Pro/Business/Enterprise at baseline)
  https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/
- Cloudflare origin IP ranges / origin protection guidance
  https://developers.cloudflare.com/fundamentals/concepts/cloudflare-ip-addresses/
  https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/

## Email deliverability

- Gmail sender guidelines
  https://support.google.com/mail/answer/81126
- Gmail sender guidelines FAQ / spam and bulk requirements
  https://support.google.com/mail/answer/14229414

## Dated competitive sources

- Yext Scout / API + MCP
  https://www.yext.com/platform/scout
  https://www.yext.com/about/news-media/yext-opens-scout-visibility-intelligence-to-partners-with-the-launch-of-mcp-and-api
- Vendasta AI Search Specialist
  https://feedback.vendasta.com/changelog/now-in-beta-ai-search-specialist-your-clients-search-visibility-optimized/
- HighLevel AI Employee / Ask AI Voice / Workflow AI
  https://help.gohighlevel.com/support/solutions/articles/155000003906
  https://help.gohighlevel.com/support/solutions/articles/155000008022-how-to-use-ask-ai-voice-mode
  https://help.gohighlevel.com/support/solutions/articles/155000006100-workflow-ai-builder
- HubSpot outcome pricing
  https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-pay-when-the-task-is-complete

## OpenHands / Prime development controller references — 2026-08-10

Prime Agent official repository and docs:
- https://github.com/PrimeIntellect-ai/prime-agent
- https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/usage.md
- https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/long-running-agents.md
- https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/json.md
- https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/rpc.md

Relevant Prime facts at this baseline:
- daemon-backed background sessions; recursive child agents; autonomous limits/gates; JSON/RPC integration;
- commands/generated code run with current-user permissions; Prime explicitly says it is not a security sandbox.

OpenHands official docs:
- https://docs.openhands.dev/sdk
- https://docs.openhands.dev/sdk/guides/agent-server/overview
- https://docs.openhands.dev/sdk/guides/metrics
- https://docs.openhands.dev/sdk/guides/llm-routing
- https://docs.openhands.dev/openhands/usage/cli/headless
- https://www.openhands.dev/product/canvas

Relevant OpenHands facts at this baseline:
- SDK/Agent Server supports programmable remote isolated workspaces and agent lifecycle;
- Agent Canvas supports parallel agents in isolated Git worktrees and ACP-compatible external agents;
- SDK metrics aggregate primary and auxiliary LLM usage including cache read/write when exposed;
- headless CLI is documented as always-approve, therefore it must not be treated as an authorization/security boundary.

OpenAI GPT-5.6 current model references:
- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/docs/models/gpt-5.6-terra
- https://developers.openai.com/api/docs/models/gpt-5.6-luna
- https://developers.openai.com/api/docs/guides/latest-model

Model names, prices, caching semantics and availability are dated references only. Task classes map to replaceable model profiles rather than hardcoding these model IDs.
