# Database Tenancy and Row Level Security

## Baseline

Shared PostgreSQL with `tenant_id` and Row Level Security.

Do not create a database per tenant initially.

## Roles

- migration/owner role: schema ownership, not used by runtime;
- runtime application role: **must not own tables** and **must not have BYPASSRLS**;
- read/reporting roles as needed with explicit policies.

Use `FORCE ROW LEVEL SECURITY` where appropriate.

## Tests

Cross-tenant tests cover:
- SELECT
- INSERT
- UPDATE
- DELETE
- joins/relationships
- vector retrieval
- object metadata
- browser profiles
- credentials references
- workflows/tasks
- caches
- notifications
- audit references
- exports.

Never rely on an application filter alone.

Review foreign-key/integrity behavior carefully because database integrity operations can behave outside ordinary RLS expectations.

## Context

Set tenant/profile execution context in a transaction-safe manner. Pooling must not leak previous tenant state.
