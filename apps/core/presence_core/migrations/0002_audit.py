"""Append-only audit tables (R0-006, ADR-0038, docs/security/audit-ledger.md).

Raw SQL, not models: nothing reads these through the ORM, and the runtime role is granted INSERT (and, for tenant
events, SELECT under RLS) only, so no code path can update or delete an audit row.
"""

from django.db import migrations

from presence_core.tenancy import protect_tenant_table

# Columns shared by both tables; names match presence_core.audit.AuditEvent.
_COMMON = """
    id uuid PRIMARY KEY,
    occurred_at timestamptz NOT NULL,
    action text NOT NULL,
    result text NOT NULL CHECK (result IN ('success', 'denied', 'failure')),
    actor text NOT NULL,
    authority_source text, operator_context text, target text, policy_decision text, connection_id text,
    artifact_refs text[] NOT NULL DEFAULT '{}', rollback_ref text, break_glass_reason text,
    request_id text, trace_id text, workflow_id text, task_id text, action_id text,
    model text, harness text, reasoning_profile text, execution_profile_id text, development_run_id text,
    detail jsonb NOT NULL DEFAULT '{}'
"""


class Migration(migrations.Migration):
    dependencies = [("presence_core", "0001_tenant_rls_fixtures")]

    operations = [
        migrations.RunSQL(
            [
                "CREATE SCHEMA audit",
                f"CREATE TABLE audit.tenant_event (tenant_id uuid NOT NULL, profile_id text, {_COMMON})",
                "CREATE INDEX tenant_event_tenant_time ON audit.tenant_event (tenant_id, occurred_at)",
                f"CREATE TABLE audit.platform_event ({_COMMON})",
                "CREATE INDEX platform_event_time ON audit.platform_event (occurred_at)",
                "GRANT USAGE ON SCHEMA audit TO presence_app",
                "GRANT SELECT, INSERT ON audit.tenant_event TO presence_app",
                # shortcut: platform events are read as the owner role until an operator audit-reader role exists.
                "GRANT INSERT ON audit.platform_event TO presence_app",
            ],
            reverse_sql=["DROP SCHEMA audit CASCADE"],
        ),
        protect_tenant_table("audit.tenant_event"),
    ]
