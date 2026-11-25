# Attention, Opportunities, Presence Health and AI Visibility

## Attention model

`AttentionItem.priority`:
- URGENT
- IMPORTANT
- NORMAL
- BACKGROUND

The user can ask “Anything important?” and receive a synthesized answer across modules.

## Opportunity Engine

Central questions:
1. Where is the profile underrepresented, incorrect, stale or invisible?
2. Given current goals and state, what is the highest-value next meaningful action?

Inputs may include:
- analytics;
- CRM/sales;
- search;
- AI search;
- social/local/reviews;
- competitors;
- trends/news/pricing;
- support/calls;
- explicit goals;
- current work.

Initial implementation: rules + scoring + LLM reasoning.

Opportunity fields:
- evidence/source finding;
- impact;
- confidence;
- effort;
- estimated cost;
- expected benefit;
- relevant skills;
- tenant goal;
- freshness;
- status.

## Presence Health

Decompose into explainable components such as:
- identity completeness;
- discoverability;
- trust;
- consistency;
- traditional search;
- AI visibility;
- local/social presence;
- reputation;
- conversion readiness;
- content authority.

Scoring formula must be versioned. Formula changes must not silently imply a customer regressed.

## AI visibility

AI search is stochastic. Do not claim deterministic “rank #3 in ChatGPT.”

Measure:
`Query Set × Location × Language × Provider × Repeated Samples`

Metrics:
- mention rate;
- citation rate;
- visibility share;
- sentiment;
- factual accuracy;
- competitor win rate;
- confidence.

Keep raw sample evidence and methodology.
