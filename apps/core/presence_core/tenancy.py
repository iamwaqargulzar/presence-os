"""Tenant context and protected-table declarations (R0-003, docs/security/database-tenancy-rls.md).

Every query on a tenant table runs inside `tenant_context()`. The tenant is a transaction-scoped setting
(`set_config(..., true)`), so it ends with the transaction and a reused connection cannot carry it into the
next request (ADR-0033 section 5). With no tenant set, policies match no row and reject every write.
"""

import logging
import re
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import UUID

from django.db import DEFAULT_DB_ALIAS, DatabaseError, connections, migrations, transaction

from presence_core.observability import correlate

TENANT_SETTING = "presence.tenant_id"
_CURRENT_TENANT = f"NULLIF(current_setting('{TENANT_SETTING}', true), '')::uuid"
_TABLE_NAME = re.compile(r"^([a-z_][a-z0-9_]{0,62}\.)?[a-z_][a-z0-9_]{0,62}$")  # optional schema
_INSUFFICIENT_PRIVILEGE = "42501"  # SQLSTATE for an RLS write rejection or a missing grant

logger = logging.getLogger("presence.rls")


class MigrateWithMigratorOnly:
    """Database router: schema changes run only as the migration role, never as the runtime role."""

    def allow_migrate(self, db: str, app_label: str, **hints: Any) -> bool:
        return db == "migrator"


@contextmanager
def tenant_context(tenant_id: UUID, using: str = DEFAULT_DB_ALIAS) -> Iterator[None]:
    """Run the block in a transaction (or savepoint) that sees only `tenant_id`'s rows.

    Nested use restores the outer tenant on exit; on error the rollback restores it.
    """
    with transaction.atomic(using=using), correlate(tenant_id=tenant_id):
        with connections[using].cursor() as cursor:
            cursor.execute("SELECT coalesce(current_setting(%s, true), '')", [TENANT_SETTING])
            (previous,) = cursor.fetchone()
            cursor.execute("SELECT set_config(%s, %s, true)", [TENANT_SETTING, str(tenant_id)])
        try:
            yield
        except DatabaseError as error:
            sqlstate = getattr(error.__cause__, "sqlstate", None)
            if sqlstate == _INSUFFICIENT_PRIVILEGE:
                # Never log row contents; the request ID is added by the JSON formatter.
                logger.warning("rls_denied", extra={"fields": {"tenant_id": str(tenant_id), "sqlstate": sqlstate}})
            raise
        with connections[using].cursor() as cursor:
            cursor.execute("SELECT set_config(%s, %s, true)", [TENANT_SETTING, previous])


def current_tenant_id(using: str = DEFAULT_DB_ALIAS) -> UUID | None:
    with connections[using].cursor() as cursor:
        cursor.execute("SELECT nullif(current_setting(%s, true), '')", [TENANT_SETTING])
        (value,) = cursor.fetchone()
    return UUID(value) if value else None


def protect_tenant_table(table: str) -> migrations.RunSQL:
    """Migration operation: enable and FORCE row-level security on `table` with the tenant policy.

    Put it in the same migration that creates the table. FORCE makes the owner obey the policy too.
    """
    if not _TABLE_NAME.match(table):
        raise ValueError(f"unexpected table name: {table!r}")
    return migrations.RunSQL(
        [
            f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY",
            f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY",
            f"CREATE POLICY tenant_isolation ON {table} "
            f"USING (tenant_id = {_CURRENT_TENANT}) WITH CHECK (tenant_id = {_CURRENT_TENANT})",
        ],
        reverse_sql=[
            f"DROP POLICY tenant_isolation ON {table}",
            f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY",
            f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY",
        ],
    )


def unprotected_tenant_tables(using: str = DEFAULT_DB_ALIAS) -> list[str]:
    """Tables (any schema) with a tenant_id column that lack enabled and forced RLS or any policy."""
    with connections[using].cursor() as cursor:
        cursor.execute(
            """
            SELECT c.oid::regclass::text FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'tenant_id' AND NOT a.attisdropped
            WHERE n.nspname NOT IN ('pg_catalog', 'information_schema') AND n.nspname NOT LIKE 'pg\\_%'
              AND c.relkind IN ('r', 'p')
              AND NOT (c.relrowsecurity AND c.relforcerowsecurity
                       AND EXISTS (SELECT FROM pg_policy p WHERE p.polrelid = c.oid))
            ORDER BY 1
            """
        )
        return [name for (name,) in cursor.fetchall()]
