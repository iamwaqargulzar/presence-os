# ADR-0005 — Temporal for Durable Workflows
Status: Accepted

## Decision
Use Temporal early for long-lived wait/retry/resume/schedule workflows.

## Rationale
Approvals, delayed publication, onboarding, domain verification, campaigns and agentic work require durable state/recovery.

## Constraint
Large artifacts live outside workflow history and are referenced by ID.
