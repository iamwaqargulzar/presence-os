# Current AI Development Candidate Notes — updated 2026-08-10

This file preserves current exploration context. It is **not** an architectural lock.

## User-observed development economics

- DeepSeek V4 Flash has been experienced as extremely inexpensive for coding.
- In ReasoniX, its native cache behavior was especially effective; token caching materially improved already-low cost.
- Kimi K2.7 Code was observed as far more expensive than DeepSeek V4 Flash in the referenced coding leaderboard/economics, reinforcing the need to compare cost per successful task rather than prestige.
- Reasoning/thinking level can materially change capability and cost. The router should not run maximum reasoning on all tasks.
- Native harness behavior matters enough that the same model should be benchmarked under multiple suitable harnesses.

## Current controller/worker selection

- OpenHands-backed DevelopmentController: selected/canary for real R0 orchestration.
- Prime Agent: primary coding worker based on the 2026-08-08 controlled Presence benchmark.
- Codex, Oh My Pi, OpenCode and ReasoniX remain fallback/challenger/specialist paths.
- Do not start another broad synthetic harness campaign before product work; use real R0/R1 telemetry.

## Candidate model roles discussed

Temporary planning candidates have included:
- GPT-5.6 Sol for architecture/orchestration;
- DeepSeek V4 Flash for cheap implementation;
- DeepSeek V4 Pro as a more capable DeepSeek escalation candidate;
- Terra for senior review/integration;
- Luna for cheaper repo/CI/context work;
- Kimi/Qwen/MiniMax/etc. through broad harness pools;
- Muse models as experimental.

Any of these may be replaced after PresenceBench.

## External benchmark reference

AI Coding Daily leaderboard:
https://aicodingdaily.com/leaderboard

Use it only for model/harness capability ideas and candidate discovery.
