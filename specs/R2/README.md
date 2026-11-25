# R2 — Presence Intelligence

R2 gives the kernel a mind and a face. The operator can ask for work from a phone, schedule it, approve it and read the result. The system learns each tenant's facts, scans its public presence, scores it and proposes what to do next. R2 performs no real external side effect: every publisher, deployer and social connector is R3.

Do not implement until the R1 exit (R1-010) is accepted.

> **Status:** contracts written 2026-11-15, revision 1, before R1 is built. Each contract must be rechecked against the R1 implementation reports before its task starts. A change found then is a spec revision, not a silent edit.

## Task order

Tasks are listed in dependency order. A task may start when every task in its "Depends on" column is done.

| # | Task | Goal in one line | Depends on |
|---|---|---|---|
| 1 | [R2-001 Task, Run and Skill Runtime](R2-001-task-run-skill-runtime.md) | One way to run bounded AI work: a task, its runs, and versioned skills. | R1-010 |
| 2 | [R2-002 Memory Store and Taxonomy](R2-002-memory-store.md) | Keep preferences, decisions, summaries and task state as separate, tenant-scoped memory. | R2-001 |
| 3 | [R2-003 Canonical Knowledge, Evidence and Conflicts](R2-003-canonical-knowledge.md) | Hold each tenant's facts with evidence; outside observations never become truth by themselves. | R2-001 |
| 4 | [R2-004 Context Compiler](R2-004-context-compiler.md) | Build the smallest correct model context, with trust labels and provider-policy filtering. | R2-002, R2-003 |
| 5 | [R2-005 Conversation Shell, Intent and Director](R2-005-conversation-shell-director.md) | Turn the operator's plain words into a task, with authority decided outside the model. | R2-001, R2-004 |
| 6 | [R2-006 Console Shell, Agent Home and Client Home](R2-006-console-shell-agent-home.md) | The installable mobile web console for the operator, and the limited client view. | R2-005 |
| 7 | [R2-007 Approval Inbox and Client Request Queue](R2-007-approval-inbox-client-queue.md) | Durable approvals for the operator and client; client requests that only queue. | R2-006 |
| 8 | [R2-008 Notifications and Push](R2-008-notifications-push.md) | Tell the operator about approvals, failures and watch results, without nagging. | R2-006, R2-007 |
| 9 | [R2-009 Task Scheduling](R2-009-task-scheduling.md) | Recurring tasks that prepare and wait by default; unattended only for marked low-risk work. | R2-001, R2-007, R2-008 |
| 10 | [R2-010 Safe Research](R2-010-safe-research.md) | Read the public web through the Fetch Broker and keep what was read as evidence. | R2-001, R2-003, R2-004 |
| 11 | [R2-011 Presence Scan and Presence Graph](R2-011-presence-scan-graph.md) | Measure where a tenant appears online and produce the Presence Snapshot. | R2-010 |
| 12 | [R2-012 Presence Health Scoring](R2-012-presence-health-scoring.md) | Explainable scores from versioned formulas. | R2-011 |
| 13 | [R2-013 Competitor Analysis](R2-013-competitor-analysis.md) | Find and compare competitors from public evidence. | R2-010, R2-011 |
| 14 | [R2-014 AI Visibility Measurement](R2-014-ai-visibility-measurement.md) | Measure AI-search visibility by repeated samples, never as a fixed rank. | R2-011, R2-013 |
| 15 | [R2-015 Opportunity Engine](R2-015-opportunity-engine.md) | Rank the next meaningful actions with evidence, and draft the first 30-day plan. | R2-012, R2-013, R2-014 |
| 16 | [R2-016 Attention Synthesis](R2-016-attention-synthesis.md) | One deduplicated answer to "anything important?" across all modules and tenants. | R2-007, R2-008, R2-015 |
| 17 | [R2-017 R2 Exit](R2-017-intelligence-exit.md) | Prove R2 end to end, including every negative case. | all of the above |

## What may run in parallel

- R2-002 and R2-003 after R2-001.
- R2-006 to R2-009 (console lane) beside R2-010 to R2-014 (intelligence lane), once R2-005 is done.
- Only one task at a time may add migrations to the same module (E-029).

## Coverage of the release plan

| Capability named in the documents | Contract |
|---|---|
| conversation shell, Director | R2-005 |
| operator mobile console: task requests, reports | R2-006 |
| approvals | R2-007 |
| client request/approve queue | R2-007 |
| push notifications | R2-008 |
| scheduling | R2-009 |
| Context Compiler | R2-004 |
| memory taxonomy | R2-002 |
| canonical knowledge, evidence, conflicts | R2-003 |
| safe research | R2-010 |
| Presence Scan, Presence Graph, Presence Snapshot | R2-011 |
| versioned health scoring | R2-012 |
| competitor analysis | R2-013 |
| repeated-sample AI visibility | R2-014 |
| Opportunity Engine, first 30-day plan | R2-015 |
| Attention synthesis | R2-016 |
| skill runtime, skill packs as supply chain | R2-001 |

## Not in R2

- Any real external side effect: publishing, posting, deploying, sending (R3 and R4).
- Website building and hosting (R3).
- Voice input and output. **Decision required**; see R2-005.
- CRM, email outreach, lead discovery (R4).
- Tenant export and offboarding workflow. No release contract owns it yet; see the open questions file.
