# GitHub Landscape for Presence OS — 2026-11-10

> **Read with the 2026-11-14 build preference:** product features are written in Presence OS. Where this document labels a whole application "Adopt" or "Service", read it as "Study": learn from it, do not deploy it, copy nothing. Libraries and base infrastructure are still used after dependency review. References to a sold product, plans or billing no longer apply (ADR-0030).

Dated reference intelligence, dated reference only. It does not change any ADR. A follow-up survey for the operator-run model is in [OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md](OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md).

**Method.** 38 GitHub search queries across the Presence subsystems, then live metadata (stars, licence, last push, archived flag) for about 100 candidate repositories through the GitHub API on 2026-11-10. READMEs were read for the seven closest projects. **No code was reviewed.** Treat every "fit" below as a lead to verify, and re-check licences before adopting anything: "custom" means GitHub could not classify the licence, which usually signals a fair-code, open-core or mixed licence.

**Reuse labels**
- **Adopt** — permissive licence, fits the stack, use as a dependency or side service.
- **Service** — copyleft (AGPL/GPL); only safe to run unmodified as a separate service, or study.
- **Study** — take the design, not the code.
- **Avoid** — archived or stale.

## 1. Headline findings

1. **Nobody open-source builds the whole thing.** No project combines canonical truth, deterministic authority, multi-tenant isolation, execution and hosting. The closest are partial: Ansvisor (visibility → actions → agent-drafted fixes), GEOFlow (knowledge → AI content → quality gate → human review → multi-site distribution), Paperclip (agent "company" with budgets, approvals and governance) and Postiz (social execution).
2. **Marketing know-how is now a commodity.** Skill packs such as `coreyhaines31/marketingskills` (59k stars) and `AgriciDaniel/claude-seo` (28k) package SEO/GEO/CRO playbooks as plain files under MIT. Presence should not hand-write these; its `skill-manifest` contract should be able to import them. The defensible part of Presence is the kernel (authority, tenancy, truth, audit), which supports the R0/R1-first sequence.
3. **AI-visibility tracking has several small open implementations** (Limelit Open, GetCito, geo-aeo-tracker, OneGlanse, Ansvisor). All are under 500 stars, so they are references for metric definitions and sampling, not foundations.
4. **Much of R0/R1 plumbing exists as mature permissive projects**: SSRF egress proxy, usage metering, LLM gateway, auth, policy engines, voice, crawling, sandboxing. Section 3 lists where a task contract could shrink.
5. **There is no mature Django + PostgreSQL RLS library.** `django-tenants` is schema-per-tenant and `django-multitenant` targets Citus. R0-003 building its own RLS helper is justified.
6. **Churn is real.** TensorZero, Daytona and Oso are archived; `bolt.new` has not been pushed since 2024-12. Pin versions and keep adapters thin, as the constitution already requires.

## 2. Closest whole-product analogues

| Project | Stars | Licence | What to take from it |
|---|---|---|---|
| [ansvisor/ansvisor](https://github.com/ansvisor/ansvisor) | 236 | MIT | Closest to the Presence loop: signals → prioritised Action Center → Content Agent drafts → humans approve. Study its action and opportunity model against `opportunity.schema.json`. |
| [yaojingang/GEOFlow](https://github.com/yaojingang/GEOFlow) | 4,056 | AGPL-3.0 | Service/Study. Full GEO pipeline with AI quality gate, human release and multi-site distribution; keeps evidence per step. PHP; docs mainly Chinese. |
| [paperclipai/paperclip](https://github.com/paperclipai/paperclip) | 112,679 | MIT | Study. Agent org chart, budgets, approvals and review gates, cost tracking. Relevant to Director Agent design and to the development factory. |
| [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | 167,529 | MIT | Role prompt library for an "AI agency". Content source for agent/skill definitions only. |
| [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) | 41,220 | AGPL-3.0 | Service. The leading open social scheduler; candidate execution backend behind the Action Broker in R3. |
| [langchain-ai/social-media-agent](https://github.com/langchain-ai/social-media-agent) | 3,006 | MIT | Study. Small, readable human-in-the-loop publish flow with an approval inbox. |
| [vercel/platforms](https://github.com/vercel/platforms) | 6,723 | none stated | Study. Minimal Next.js multi-tenant subdomain routing; reference for R1-005 Edge lookup. No licence file, so do not copy code. |

## 3. By Presence subsystem

### Kernel: tenancy, identity, authorization (R0-003, R0-004, R1-001, R1-002)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [pennersr/django-allauth](https://github.com/pennersr/django-allauth) | 10,383 | MIT | Adopt | Answers the open "authentication library" decision in R0-004. |
| [supabase/supabase](https://github.com/supabase/supabase) | 114,722 | Apache-2.0 | Study | Best public body of RLS policy patterns and tests. |
| [django-tenants/django-tenants](https://github.com/django-tenants/django-tenants) | 1,901 | MIT | Study | Schema-per-tenant; conflicts with ADR-0004. Useful for middleware ideas only. |
| [citusdata/django-multitenant](https://github.com/citusdata/django-multitenant) | 824 | MIT | Study | Tenant-context propagation in the ORM. |
| [openfga/openfga](https://github.com/openfga/openfga) | 6,122 | Apache-2.0 | Study | Zanzibar-style relationship model; likely more than R1 needs. |
| [cerbos/cerbos](https://github.com/cerbos/cerbos) | 4,653 | Apache-2.0 | Study | Policy-as-files with tests; good model for the versioned risk table in R1-002. |
| [open-policy-agent/opa](https://github.com/open-policy-agent/opa) | 12,453 | Apache-2.0 | Study | General policy engine; consider only if policies outgrow code. |
| [apache/casbin](https://github.com/apache/casbin) | 20,489 | Apache-2.0 | Study | RBAC/ABAC library with a Python port. |
| [Justin0504/Aegis](https://github.com/Justin0504/Aegis) | 523 | MIT | Study | Runtime policy enforcement, signed audit trail, approvals and kill switch for agents: the nearest thing to an Action Broker. |
| [humanlayer/humanlayer](https://github.com/humanlayer/humanlayer) | 12,847 | Apache-2.0 | Study | Began as human-approval tooling; now positioned around coding agents. |

A separate authorization server adds an operational dependency the modular-monolith rule argues against. Default recommendation: implement RBAC in code, borrow Cerbos's test-per-policy discipline.

### Security brokers (R0-008, R0-012)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [stripe/smokescreen](https://github.com/stripe/smokescreen) | 1,396 | MIT | Adopt | Egress proxy that blocks private/internal ranges, built for exactly the SSRF problem. Strong candidate to be the Fetch Broker's network layer and the development sandbox's egress control. |
| [openbao/openbao](https://github.com/openbao/openbao) | 8,951 | MPL-2.0 | Adopt | Already chosen (ADR-0015). |
| [Infisical/infisical](https://github.com/Infisical/infisical) | 30,394 | custom | Study | Easier operator experience than OpenBao; licence needs reading. |
| [google/gvisor](https://github.com/google/gvisor) | 19,944 | Apache-2.0 | Adopt | Already chosen (ADR-0016). |
| [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | 14,788 | Apache-2.0 | Study | Sandbox API design for agent code execution. |
| [retracedhq/retraced](https://github.com/retracedhq/retraced) | 451 | Apache-2.0 | Study | Audit-log service with embeddable viewer; event model reference for R0-006. |

### Workflows and agent runtime (R0-005, R2)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [temporalio/temporal](https://github.com/temporalio/temporal) | 24,294 | MIT | Adopt | Already chosen (ADR-0005). |
| [temporal-community/temporal-ai-agent](https://github.com/temporal-community/temporal-ai-agent) | 790 | MIT | Study | Python agent loop inside a workflow, tool calls needing human confirmation, history compaction, LiteLLM. The best starting reference for the R0-005 human-wait workflow. Last push 2026-03. |
| [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | 21,111 | MIT | Adopt (candidate) | Typed Python agent framework; fits Django and strong-contract rules. Verify its current Temporal integration. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 44,720 | MIT | Study | Interrupt/resume approval pattern. Overlaps Temporal. |
| [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | 30,589 | MIT | Study | Handoffs and guardrails API design. |
| [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet), [triggerdotdev/trigger.dev](https://github.com/triggerdotdev/trigger.dev) | 8,257 / 16,737 | MIT / Apache-2.0 | Study | Alternatives to Temporal; no reason to switch. |

### AI gateway, observability, evaluation (R0-007, R1-012)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 63,004 | custom (mixed) | Adopt as one adapter | Provider normalisation, budgets and fallbacks. Keep it behind the Capability Gateway interface, never imported by modules. |
| [maximhq/bifrost](https://github.com/maximhq/bifrost) | 9,462 | Apache-2.0 | Study | Clean-licence gateway alternative. |
| [Portkey-AI/gateway](https://github.com/Portkey-AI/gateway) | 13,357 | MIT | Study | Last push 2026-05; activity slowing. |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 37,222 | custom (mixed) | Service | Tracing, cost and evals for LLM calls. Tenant content would flow into it, so treat as a tenant-data store. |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 27,003 | MIT | Adopt | Prompt-injection and red-team suites for PresenceBench's security set. |
| [UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) | 3,212 | MIT | Adopt (candidate) | Python evaluation framework; could be the PresenceBench runner. |
| tensorzero/tensorzero | 11,705 | Apache-2.0 | Avoid | Archived. |

### Billing and metering (R1-004)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [openmeterio/openmeter](https://github.com/openmeterio/openmeter) | 2,441 | Apache-2.0 | Study/Adopt | Usage metering and entitlements for AI workloads; closest to the usage-ledger and AI Compute Unit design. Adds Kafka/ClickHouse-class dependencies, so check against "do not overengineer". |
| [getlago/lago](https://github.com/getlago/lago) | 10,786 | AGPL-3.0 | Service | Usage-based billing with wallets and prepaid credits: maps to the Service Wallet. |
| [polarsource/polar](https://github.com/polarsource/polar) | 10,468 | Apache-2.0 | Study | Python billing platform; relevant to the open "payment processor" decision. |
| [flexprice/flexprice](https://github.com/flexprice/flexprice) | 6,877 | AGPL-3.0 | Study | Credits and usage pricing model. |

### Connections and integrations (R1-007, R3+)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [NangoHQ/nango](https://github.com/NangoHQ/nango) | 13,165 | custom | Study | OAuth for hundreds of APIs with token refresh: effectively a Connection Broker. Its provider configuration catalogue is the valuable part. |
| [ComposioHQ/composio](https://github.com/ComposioHQ/composio) | 31,004 | MIT | Study | Tool catalogue with managed auth; hosted dependency in practice. |
| [activepieces/activepieces](https://github.com/activepieces/activepieces) | 25,455 | custom | Study | Connector "piece" format as a model for execution adapters. |
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | 209,954 | custom (fair-code) | Study | Not embeddable in a commercial SaaS without a licence. |

Adopting a third-party token store conflicts with "credentials only behind the Secrets Broker". Use these for provider metadata and flow design.

### Domains and hosting (R1-005, R1-006, R1-011, R3)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [caddyserver/caddy](https://github.com/caddyserver/caddy) | 78,935 | Apache-2.0 | Adopt | Already chosen. Its on-demand TLS with an "ask" endpoint is a self-hosted alternative to Cloudflare for SaaS for custom domains. |
| [coollabsio/coolify](https://github.com/coollabsio/coolify) | 65,860 | Apache-2.0 | Study/Service | Deploy, preview, rollback and domains for apps. Presence could drive one through its API in R3 instead of writing a deployer. |
| [Dokploy/dokploy](https://github.com/Dokploy/dokploy) | 38,347 | custom | Study | Same role, TypeScript. |
| [dokku/dokku](https://github.com/dokku/dokku) | 32,222 | MIT | Study | Simplest buildpack/Docker PaaS; scriptable. |

### Website and app generation (R3)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [payloadcms/payload](https://github.com/payloadcms/payload) | 45,745 | MIT | Adopt (candidate) | Next.js-native CMS; a structured content backend an agent can edit safely. |
| [puckeditor/puck](https://github.com/puckeditor/puck) | 13,667 | MIT | Adopt (candidate) | React visual editor over JSON page data. JSON pages are hashable artifacts, which suits artifact-bound approvals. |
| [firecrawl/open-lovable](https://github.com/firecrawl/open-lovable) | 28,883 | MIT | Study | Clone/recreate an existing site as React: relevant to "improve my current website". |
| [dyad-sh/dyad](https://github.com/dyad-sh/dyad) | 22,251 | custom | Study | Local AI app builder; prompt and edit-loop design. |
| [stackblitz-labs/bolt.diy](https://github.com/stackblitz-labs/bolt.diy) | 20,068 | MIT | Study | Any-LLM app builder. |
| [onlook-dev/onlook](https://github.com/onlook-dev/onlook) | 27,156 | Apache-2.0 | Study | Visual editing of real React code. |
| [webstudio-is/webstudio](https://github.com/webstudio-is/webstudio) | 9,160 | AGPL-3.0 | Service | Webflow-style builder. |
| [GrapesJS/grapesjs](https://github.com/GrapesJS/grapesjs) | 26,401 | custom (BSD-style) | Study | Mature page-builder framework. |
| stackblitz/bolt.new | 16,589 | MIT | Avoid | No push since 2024-12. |

### SEO, AEO/GEO and AI visibility (R2 Presence Scan, R3)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | 59,446 | MIT | Adopt content | Marketing skill pack. |
| [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | 27,750 | MIT | Adopt content | 26 sub-skills covering technical SEO, schema, E-E-A-T, GEO. |
| [Ryze-AI-Adgent/open-seo-mcp-skills](https://github.com/Ryze-AI-Adgent/open-seo-mcp-skills) | 9,054 | MIT | Study | SEO MCP server: keyword research, rank tracking, audits. |
| [limelit-co/open](https://github.com/limelit-co/open) | 438 | Apache-2.0 | Study | Self-hosted AI visibility tracking; documents "how the numbers are computed" and cost. Best reference for the stochastic sampling the Decision Register requires. |
| [danishashko/geo-aeo-tracker](https://github.com/danishashko/geo-aeo-tracker), [oneglanse/oneglanse](https://github.com/oneglanse/oneglanse), [ai-search-guru/getcito…](https://github.com/ai-search-guru/getcito-worlds-first-open-source-aio-aeo-or-geo-tool) | 324 / 254 / 426 | MIT | Study | Alternative tracker implementations. |
| [Auriti-Labs/geo-optimizer-skill](https://github.com/Auriti-Labs/geo-optimizer-skill) | 1,300 | MIT | Study | Audits whether AI engines can read and cite a site. |
| [towfiqi/serpbear](https://github.com/towfiqi/serpbear) | 2,174 | MIT | Study | Rank tracking data model. |
| [karust/openserp](https://github.com/karust/openserp) | 1,564 | MIT | Study | Self-hosted multi-engine search API. Scraping search engines raises the platform-policy rule in `AGENTS.md`. |
| [AnswerDotAI/llms-txt](https://github.com/AnswerDotAI/llms-txt) | 2,682 | Apache-2.0 | Adopt | Reference for generating `llms.txt` on hosted properties. |

No open project was found for local listings, Google Business Profile or review management.

### Research, crawling, browser (R2, R4)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | 87,156 | Apache-2.0 | Adopt (candidate) | Python crawler producing LLM-ready text; run it behind the Fetch Broker. |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 200,211 | AGPL-3.0 | Service | Most capable crawler/extractor. |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | 120,462 | MIT | Study | Browser agent; note its cloud offers "stealth", which Presence must not use. |
| [browserbase/stagehand](https://github.com/browserbase/stagehand) | 25,992 | MIT | Study | Playwright plus natural-language actions. |
| [Skyvern-AI/skyvern](https://github.com/Skyvern-AI/skyvern) | 23,376 | AGPL-3.0 | Study | Browser workflows. |

### Knowledge and memory (R2)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [getzep/graphiti](https://github.com/getzep/graphiti) | 32,694 | Apache-2.0 | Study | Facts with validity intervals and supersession: close to the Fact → SUPERSEDED model. Needs a graph database, which the project has ruled out for now. |
| [mem0ai/mem0](https://github.com/mem0ai/mem0) | 68,719 | Apache-2.0 | Study | Memory extraction and update prompts; supports pgvector. |
| [topoteretes/cognee](https://github.com/topoteretes/cognee) | 33,192 | Apache-2.0 | Study | Knowledge pipelines. |
| [letta-ai/letta](https://github.com/letta-ai/letta) | 25,396 | Apache-2.0 | Study | Stateful agent memory blocks. |

### Voice, CRM, support, email (R2 voice shell, R4)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | 17,165 | BSD-2-Clause | Adopt (candidate) | Python voice pipeline with pluggable local STT/TTS; fits the private GPU server. |
| [livekit/agents](https://github.com/livekit/agents) | 15,159 | Apache-2.0 | Adopt (candidate) | Realtime voice agents and telephony; candidate for the voice receptionist. |
| [twentyhq/twenty](https://github.com/twentyhq/twenty) | 60,716 | custom | Study | Modern CRM data model. |
| [chatwoot/chatwoot](https://github.com/chatwoot/chatwoot) | 39,527 | custom | Study | Omnichannel inbox. |
| [knadh/listmonk](https://github.com/knadh/listmonk) | 24,230 | AGPL-3.0 | Service | Newsletter sending with suppression lists. |
| [calcom/cal.diy](https://github.com/calcom/cal.diy) | 49,868 | MIT | Study | Booking property type. |

### Development factory (R0-011, R0-012)

| Project | Stars | Licence | Label | Note |
|---|---|---|---|---|
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | 93,068 | MIT | Adopt | Already chosen as controller (ADR-0025). |
| [PrimeIntellect-ai/prime-agent](https://github.com/PrimeIntellect-ai/prime-agent) | 22,647 | custom | Adopt | Already chosen as worker. Licence is unclassified: read it. Describes itself as "self-improving", which is the behaviour the specs require to be disabled. |
| [BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban) | 28,633 | Apache-2.0 | Study | Task board that runs coding agents in isolated worktrees with review: overlaps much of R0-011's lease/worktree/review scope. |
| [stablyai/orca](https://github.com/stablyai/orca) | 120,566 | MIT | Study | Runs a fleet of coding agents on your own subscriptions. |
| [paperclipai/paperclip](https://github.com/paperclipai/paperclip) | 112,679 | MIT | Study | Budgets, approvals and audit for agent teams. |

R0-011 specifies a custom controller with about a dozen operations. Before building it, compare against vibe-kanban and orca: either may already provide lease, worktree and review lifecycle, leaving only the Prime adapter and independent gate runner to write.

## 4. What this suggests for the plan

1. **Keep the kernel in-house.** Authorization Service, Action Broker, RLS and audit have no adoptable equivalent and are the product's differentiation.
2. **Shrink R0-008** by putting Smokescreen under the Fetch Broker.
3. **Resolve open decisions with existing projects:** django-allauth (auth), LiteLLM as the first gateway adapter, promptfoo and Inspect for PresenceBench.
4. **Re-examine R0-011's build-versus-adopt balance** against vibe-kanban and orca before writing a controller.
5. **Plan R3 as integration, not construction:** Payload or Puck for site content, an existing PaaS for deploys, Postiz for social, skill packs for marketing know-how. Each sits behind the Action Broker.
6. **Use Limelit Open and Ansvisor** as the reference designs for Presence Scan metrics and the Opportunity/Action loop.
7. **Add a licence gate** to the dependency policy: AGPL projects run only as unmodified separate services; "custom" licences need a written review.

## 5. Limits of this survey

- Stars measure attention, not quality or security.
- Licence labels are GitHub's classification, not legal review.
- Only seven READMEs were read; no architecture or code was inspected.
- Closed-source competitors are covered separately in the competitive research notes.
- Search was GitHub-only and English-biased.
