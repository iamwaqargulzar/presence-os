# Database Tenancy and Row Level Security

## Baseline

Shared PostgreSQL with `tenant_id` and Row Level Security. Do not create a database or schema per tenant.

Built in R0-003; decisions in [ADR-0036](../adrs/ADR-0036-postgres-roles-and-tenant-context.md). Code: `apps/core/presence_core/tenancy.py`, `apps/core/presence_core/rls_testing.py`, `infra/postgres/roles.sh`.

## Roles

| Role | Used by | Attributes |
|---|---|---|
| bootstrap superuser (`POSTGRES_USER`) | `infra/postgres/roles.sh` only | creates the two roles below; Django never connects as it |
| `presence_migrator` | Django alias `migrator`: `manage.py migrate --database migrator` | owns the database and every table; NOSUPERUSER, NOBYPASSRLS, NOCREATEROLE. CREATEDB locally and in CI only, so Django can create test databases; never in production |
| `presence_app` | Django alias `default`: every request and job | owns nothing; NOSUPERUSER, NOBYPASSRLS, NOCREATEDB, NOCREATEROLE, NOINHERIT; not a member of `presence_migrator`; SELECT/INSERT/UPDATE/DELETE on tables (no TRUNCATE) through default privileges |

- A database router (`MigrateWithMigratorOnly`) lets migrations run only on the `migrator` alias.
- Default privileges are granted in `presence_core` migration 0001, so they cover tables created after it. Tables created earlier (`django_migrations`, `django_content_type`) are not readable by `presence_app`; a later task that needs them grants them in a migration.
- Read/reporting roles: placeholder only. A future reporting role gets its own policies and is never given BYPASSRLS.
- `roles.sh` is idempotent and runs on every `make services-up`, so a password change in `.env` is applied on the next run.

## Tenant context

- `tenant_context(tenant_id)` opens a transaction (a savepoint when nested) and runs `set_config('presence.tenant_id', <uuid>, true)`. The setting is transaction-scoped, so it ends with the transaction and a pooled or reused connection cannot carry it into the next request (ADR-0033 §5). Nested use restores the outer tenant.
- Every policy is `tenant_id = NULLIF(current_setting('presence.tenant_id', true), '')::uuid` in both USING and WITH CHECK. With no context the comparison is NULL: reads return no rows and every write is rejected (fails closed).
- Cost: two extra statements per transaction. This works with Django's persistent connections and with a transaction-mode pooler; a session-mode-only design is not needed.
- Profile is enforced in the service layer until R1 (ADR-0033).

## FORCE ROW LEVEL SECURITY

FORCE is on for every tenant table, by default and without per-table exceptions. The owner (`presence_migrator`) therefore obeys the policies too, so a data migration must also run inside `tenant_context(..., using="migrator")`. A table that needs an exception needs an ADR.

| Table | RLS | FORCE |
|---|---|---|
| `presence_core_rlsfixtureparent` (fixture, R0-003) | on | on |
| `presence_core_rlsfixturechild` (fixture, R0-003) | on | on |

## Foreign keys and integrity checks

PostgreSQL runs foreign-key checks without row security. A plain `child.parent_id → parent.id` key would accept a child pointing at another tenant's parent, and its error would reveal that the row exists. So:

- the parent gets `UNIQUE (tenant_id, id)`;
- the child gets the composite key `FOREIGN KEY (tenant_id, parent_id) REFERENCES parent (tenant_id, id)`, added with `RunSQL`; the Django field uses `db_constraint=False`.

Unique constraints have the same property: a unique violation can reveal another tenant's value. Include `tenant_id` in every unique constraint on a tenant table, unless global uniqueness is the point.

## How to add a tenant table

1. Give the model a non-null `tenant_id = models.UUIDField()`.
2. In the migration that creates the table, add `protect_tenant_table("<table>")` from `presence_core.tenancy` right after `CreateModel`. It enables and forces RLS and creates the `tenant_isolation` policy, with a reverse.
3. Reference other tenant tables only through a composite `(tenant_id, …)` foreign key, as above.
4. Write a test class on `TenantIsolationTestCase` (`presence_core.rls_testing`): list the table in `tenant_tables`, call `assert_crud_isolated(Model, make_fields)` and add join tests for its relationships.
5. Run all queries inside `tenant_context()`.

`test_every_tenant_table_is_protected` fails if any table with a `tenant_id` column lacks enabled and forced RLS or a policy.

## Observability

A rejected write raises SQLSTATE 42501. `tenant_context` logs it as `rls_denied` on logger `presence.rls` with `tenant_id` and `sqlstate` (the JSON formatter adds `request_id`), never the row contents. Reads are filtered, not rejected, so they produce no log.

## Caches (E-044)

Any cache shared between requests is keyed by tenant ID (and profile, from R1). A cache key without the tenant is a defect, the same as a missing policy.

## Tests

`apps/core/presence_core/tests.py` runs as `presence_app` against real PostgreSQL in CI. Cross-tenant tests cover SELECT, INSERT, UPDATE, DELETE, joins/relationships, missing context, connection reuse and nested contexts, the runtime role's attributes, and detection of an unprotected table. Later modules extend the suite to:

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
