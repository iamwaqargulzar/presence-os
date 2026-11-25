# Agent, Skill, Tool, Connector and Provider Model

## Avoid one giant agent

The system may implement specialist roles:
- Presence Director
- Research
- Brand
- SEO
- AEO/GEO/AI Presence
- Content
- Web Development
- QA
- Social
- Image/Video
- Community
- Local SEO/GBP
- Analytics/CRO
- Reputation
- Security
- Email/CRM
- Paid Media
- PR
- Ecommerce
- Reporting
- Career/LinkedIn
- Opportunity
- Support
- Voice
- Finance Ops
- Platform Engineer
- Ecosystem Watch

Customers should not be forced to understand this catalog.

## Skill levels

1. Tool skills — small provider/tool operations.
2. Domain skills — coherent domain capability.
3. Composite business skills — multi-step outcome-oriented behavior.

## Skill manifest

Each skill is versioned and declares:
- input/output schemas;
- required capabilities/providers;
- permissions;
- risk class;
- expected/max cost;
- token/tool/time limits;
- retry/checkpoint/cache policy;
- evaluation suite;
- metrics;
- global/tenant/platform scope;
- commercial licensing if relevant.

Skills are independently testable/releasable.

Tenant-created skills may later be promoted globally only through review.

## Capability over model names

Skills ask for capabilities such as:
- high-quality reasoning;
- cheap classification;
- coding;
- vision;
- image generation;
- realtime voice;
rather than hard-coded model IDs.
