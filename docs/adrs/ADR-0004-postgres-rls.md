# ADR-0004 — Shared PostgreSQL + Row Level Security
Status: Accepted

## Decision
Use shared PostgreSQL with tenant_id and RLS initially.

## Constraints
Runtime role does not own protected tables and has no BYPASSRLS. FORCE RLS where appropriate. Cross-tenant tests are release gates.
