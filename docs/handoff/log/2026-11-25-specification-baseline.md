# Session Handoff — 2026-11-25 — Specification baseline

- Date: 2026-11-25 (session ran from 2026-11-14)
- Phase / release: specification, before R0
- Task contract(s): all of `specs/`; no implementation task
- Starting commit: no repository
- Ending commit: Git initialised on `main`; first commit pending the owner's approval
- Worker / model: Claude Code (desktop app), Claude models

## Done
- Operator-run model adopted ([ADR-0030](../../adrs/ADR-0030-operator-run-agency-deployment.md)); social connectors in-house ([ADR-0031](../../adrs/ADR-0031-postiz-self-hosted-social-publishing.md)).
- Open-source survey for the new objective, including a direct read of AgenticOS: [research note](../../research/OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md). Edge cases E-091 to E-094 added.
- Toolchain and versions ([ADR-0032](../../adrs/ADR-0032-toolchain-versions-and-repository.md)); R0 and R1 technical defaults ([ADR-0033](../../adrs/ADR-0033-technical-defaults-for-r0-and-r1.md)); three contract schema gaps fixed.
- Ten owner questions answered and recorded (see "Decided" below).
- R2 (17) and R3 (14) task contracts written in a separate session.
- Repository structure cleaned; documentation standards, handoff protocol, contribution and security policies added.

## Decided
All recorded in [DECISION_REGISTER.md](../../DECISION_REGISTER.md) and [ASSUMPTIONS_AND_OPEN_QUESTIONS.md](../../ASSUMPTIONS_AND_OPEN_QUESTIONS.md):
- scheduled tasks prepare and wait; unattended only per low-risk task, on API credentials;
- phone access through the installable web console with push notifications;
- Meta first, then LinkedIn;
- low-cost model DeepSeek V4.1 Flash for now, as configuration;
- clients without Google create an account on their own email, or get no login;
- clients cannot revoke or pause the operator's access;
- budgets in USD, rupees for reading; caps USD 20 / 30 / 150 a month;
- console at `console.iamwaqargulzar.com`; nothing tenant-generated under that domain;
- interim backup copy on an encrypted USB drive, cloud storage before client production data;
- personal profile is its own tenant;
- model gateway built in-house; Claude Code primary worker, Prime second.

## Not finished
- First Git commit and the private GitHub repository.

## Not checked
- Versions and tool names were not checked against official sources.
- R2 and R3 contracts had no second review.

## Next step
Make the first commit, create the private GitHub repository, then start R0-001 in a new session from [STATUS.md](../STATUS.md).

## Owner decisions waiting
See [STATUS.md](../STATUS.md).
