import io
import json
import logging
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import UUID

from django.core.management import call_command
from django.db import DatabaseError, connections, transaction
from django.test import SimpleTestCase, tag

from presence_core.audit import AuditEvent, append_audit
from presence_core.models import RlsFixtureChild, RlsFixtureParent
from presence_core.observability import REDACTED, JsonFormatter, correlate, redact
from presence_core.rls_testing import TENANT_A, TENANT_B, TenantIsolationTestCase
from presence_core.tenancy import current_tenant_id, tenant_context, unprotected_tenant_tables


class HealthTests(SimpleTestCase):
    def test_health_responds_ok_with_nothing_else(self) -> None:
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_rejects_writes(self) -> None:
        self.assertEqual(self.client.post("/healthz").status_code, 405)


class RequestIdTests(SimpleTestCase):
    def test_generates_request_id_and_logs_json(self) -> None:
        with self.assertLogs("presence.request", level="INFO") as logs:
            response = self.client.get("/healthz")
        request_id = response["X-Request-ID"]
        self.assertRegex(request_id, r"^[0-9a-f]{32}$")
        record = logs.records[0]
        self.assertEqual(record.fields["status"], 200)  # type: ignore[attr-defined]
        line = json.loads(JsonFormatter().format(record))
        self.assertEqual(line["path"], "/healthz")

    def test_keeps_safe_incoming_id(self) -> None:
        response = self.client.get("/healthz", headers={"X-Request-ID": "abc-123"})
        self.assertEqual(response["X-Request-ID"], "abc-123")

    def test_replaces_unsafe_incoming_id(self) -> None:
        response = self.client.get("/healthz", headers={"X-Request-ID": 'x"\n{"forged":1}'})
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")

    def test_formatter_output_is_one_json_line(self) -> None:
        record = logging.LogRecord("t", logging.INFO, __file__, 1, "a\nb", None, None)
        out = JsonFormatter().format(record)
        self.assertNotIn("\n", out)
        self.assertEqual(json.loads(out)["msg"], "a\nb")


# Credential-shaped test values, generated for these tests only; none is a real secret.
SEEDED_SECRETS = {
    "bearer": "Bearer abcDEF123456ghiJKL7890",
    "password": "hunter2-not-real",
    "cookie": "sessionid=s3ss10nv4lu3notreal",
    "api_key": "sk-test" + "0123456789abcdefXYZ",
    "email": "jane.doe@example.com",
}
SEEDED_TEXT = (
    f"Authorization: {SEEDED_SECRETS['bearer']} password={SEEDED_SECRETS['password']} "
    f"Cookie: {SEEDED_SECRETS['cookie']}\nkey {SEEDED_SECRETS['api_key']} from {SEEDED_SECRETS['email']}"
)


def assert_clean(test: SimpleTestCase, text: str) -> None:
    for name, secret in SEEDED_SECRETS.items():
        test.assertNotIn(secret.split()[-1].split("=")[-1], text, name)


@contextmanager
def json_logs(name: str) -> Iterator[io.StringIO]:
    """Capture `name`'s log lines as the JsonFormatter writes them, at emit time (correlation is live then)."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logging.getLogger(name).addHandler(handler)
    try:
        yield stream
    finally:
        logging.getLogger(name).removeHandler(handler)


class RedactionTests(SimpleTestCase):
    def test_log_line_redacts_message_fields_and_exceptions(self) -> None:
        try:
            raise ValueError(SEEDED_TEXT)
        except ValueError:
            record = logging.LogRecord("t", logging.ERROR, __file__, 1, SEEDED_TEXT, None, sys.exc_info())
        record.fields = {"password": SEEDED_SECRETS["password"], "headers": {"Cookie": SEEDED_SECRETS["cookie"]}}
        line = JsonFormatter().format(record)
        assert_clean(self, line)
        entry = json.loads(line)
        self.assertEqual(entry["password"], REDACTED)
        self.assertEqual(entry["headers"], {"Cookie": REDACTED})
        self.assertGreaterEqual(entry["redactions"], 7)

    def test_ordinary_values_are_kept(self) -> None:
        value = {"path": "/healthz", "status": 200, "password": None, "note": "user 42 signed in"}
        self.assertEqual(redact(value), (value, 0))


class CorrelationTests(SimpleTestCase):
    TRACE = "4bf92f3577b34da6a3ce929d0e0e4736"

    def test_continues_valid_incoming_trace(self) -> None:
        with json_logs("presence.request") as logs:
            response = self.client.get("/healthz", headers={"traceparent": f"00-{self.TRACE}-00f067aa0ba902b7-01"})
        self.assertRegex(response["traceparent"], rf"^00-{self.TRACE}-[0-9a-f]{{16}}-01$")
        line = json.loads(logs.getvalue())
        self.assertEqual(line["trace_id"], self.TRACE)
        self.assertEqual(line["request_id"], response["X-Request-ID"])

    def test_replaces_missing_or_invalid_trace(self) -> None:
        for header in ("", "00-" + "0" * 32 + "-00f067aa0ba902b7-01", "zz-bad\n"):
            response = self.client.get("/healthz", headers={"traceparent": header} if header else {})
            self.assertRegex(response["traceparent"], r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$")
            self.assertNotIn("0" * 32, response["traceparent"])

    def test_context_ids_reach_log_lines_and_end_with_the_block(self) -> None:
        record = logging.LogRecord("t", logging.INFO, __file__, 1, "m", None, None)
        with correlate(tenant_id=TENANT_A, task_id="task-1", workflow_id=None):
            line = json.loads(JsonFormatter().format(record))
        self.assertEqual((line["tenant_id"], line["task_id"]), (str(TENANT_A), "task-1"))
        self.assertNotIn("workflow_id", line)
        self.assertNotIn("tenant_id", json.loads(JsonFormatter().format(record)))
        with self.assertRaises(ValueError):
            correlate(tenant=1).__enter__()


@tag("integration")
class DatabaseTests(SimpleTestCase):
    databases = {"migrator"}

    def test_migrations_ran_from_empty_on_the_test_database(self) -> None:
        migrator = connections["migrator"]
        self.assertTrue(migrator.settings_dict["NAME"].startswith("test_"))
        with migrator.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM django_migrations WHERE app = 'contenttypes'")
            (applied,) = cursor.fetchone()
        self.assertGreater(applied, 0)

    def test_presence_core_migrations_reverse_and_reapply(self) -> None:
        call_command("migrate", "presence_core", "zero", database="migrator", verbosity=0)
        self.assertEqual(unprotected_tenant_tables("migrator"), [])
        call_command("migrate", "presence_core", database="migrator", verbosity=0)
        self.assertEqual(unprotected_tenant_tables("migrator"), [])


@tag("integration")
class RuntimeRoleTests(TenantIsolationTestCase):
    def query(self, sql: str) -> object:
        with connections["default"].cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchone()[0]

    def test_runtime_role_is_least_privileged(self) -> None:
        self.assertEqual(self.query("SELECT current_user"), "presence_app")
        self.assertEqual(
            self.query(
                "SELECT (rolsuper, rolbypassrls, rolcreaterole, rolcreatedb) FROM pg_roles WHERE rolname = current_user"
            ),
            ("f", "f", "f", "f"),
        )
        self.assertEqual(self.query("SELECT count(*) FROM pg_class WHERE relowner = 'presence_app'::regrole"), 0)
        self.assertFalse(self.query("SELECT pg_has_role('presence_app', 'presence_migrator', 'MEMBER')"))
        self.assertFalse(self.query("SELECT has_table_privilege('presence_core_rlsfixtureparent', 'TRUNCATE')"))

    def test_every_tenant_table_is_protected(self) -> None:
        self.assertEqual(unprotected_tenant_tables(), [])


@tag("integration")
class UnprotectedTableDetectionTests(SimpleTestCase):
    databases = {"migrator"}

    def test_seeded_unprotected_table_is_detected(self) -> None:
        migrator = connections["migrator"]
        with migrator.cursor() as cursor:
            cursor.execute("CREATE TABLE rls_unprotected_probe (id int, tenant_id uuid)")
        try:
            self.assertEqual(unprotected_tenant_tables("migrator"), ["rls_unprotected_probe"])
            with migrator.cursor() as cursor:  # a policy without FORCE still counts as unprotected
                cursor.execute("ALTER TABLE rls_unprotected_probe ENABLE ROW LEVEL SECURITY")
                cursor.execute("CREATE POLICY p ON rls_unprotected_probe USING (true)")
            self.assertEqual(unprotected_tenant_tables("migrator"), ["rls_unprotected_probe"])
        finally:
            with migrator.cursor() as cursor:
                cursor.execute("DROP TABLE rls_unprotected_probe")


@tag("integration")
class TenantIsolationTests(TenantIsolationTestCase):
    tenant_tables = ("presence_core_rlsfixturechild", "presence_core_rlsfixtureparent")

    def test_parent_crud_is_isolated(self) -> None:
        self.assert_crud_isolated(RlsFixtureParent, lambda tenant: {"name": f"p-{tenant}"})

    def test_child_crud_is_isolated(self) -> None:
        parents = {t: self.seed(t, RlsFixtureParent, name="p") for t in (TENANT_A, TENANT_B)}
        self.assert_crud_isolated(RlsFixtureChild, lambda tenant: {"parent_id": parents[tenant].pk, "note": "c"})

    def test_joins_show_only_own_rows(self) -> None:
        own = self.seed(TENANT_A, RlsFixtureParent, name="own")
        other = self.seed(TENANT_B, RlsFixtureParent, name="other")
        self.seed(TENANT_A, RlsFixtureChild, parent_id=own.pk, note="own")
        self.seed(TENANT_B, RlsFixtureChild, parent_id=other.pk, note="other")
        with tenant_context(TENANT_A):
            rows = list(RlsFixtureChild.objects.select_related("parent").values_list("note", "parent__name"))
            self.assertEqual(rows, [("own", "own")])
            self.assertEqual(list(RlsFixtureParent.objects.filter(rlsfixturechild__note="other")), [])
            self.assertEqual(RlsFixtureChild.objects.filter(parent_id=other.pk).count(), 0)

    def test_child_cannot_reference_other_tenants_parent(self) -> None:
        other = self.seed(TENANT_B, RlsFixtureParent, name="other")
        with self.assertRaises(DatabaseError), tenant_context(TENANT_A):
            RlsFixtureChild.objects.create(tenant_id=TENANT_A, parent_id=other.pk, note="probe")

    def test_reused_connection_does_not_leak_tenant(self) -> None:
        self.seed(TENANT_A, RlsFixtureParent, name="a")
        self.seed(TENANT_B, RlsFixtureParent, name="b")
        conn = connections["default"]
        with tenant_context(TENANT_A):
            pid = self.backend_pid()
            self.assertEqual(list(RlsFixtureParent.objects.values_list("name", flat=True)), ["a"])
        self.assertIsNone(current_tenant_id())
        self.assertEqual(RlsFixtureParent.objects.count(), 0)
        with tenant_context(TENANT_B):
            self.assertEqual(self.backend_pid(), pid, "expected the same server connection")
            self.assertEqual(list(RlsFixtureParent.objects.values_list("name", flat=True)), ["b"])
            with tenant_context(TENANT_A):  # nested context restores the outer tenant
                self.assertEqual(current_tenant_id(), TENANT_A)
            self.assertEqual(current_tenant_id(), TENANT_B)
        self.assertIsNone(current_tenant_id())
        self.assertTrue(conn.is_usable())

    def test_context_cleared_after_error(self) -> None:
        with self.assertRaises(RuntimeError), tenant_context(TENANT_A):
            raise RuntimeError("boom")
        self.assertIsNone(current_tenant_id())
        with transaction.atomic():  # a plain transaction on the same connection has no tenant either
            self.assertIsNone(current_tenant_id())
            self.assertEqual(RlsFixtureParent.objects.count(), 0)

    def test_rls_denial_is_logged_without_row_data(self) -> None:
        with self.assertLogs("presence.rls", level="WARNING") as logs, self.assertRaises(DatabaseError):
            with tenant_context(TENANT_A):
                RlsFixtureParent.objects.create(tenant_id=TENANT_B, name="secret-row-content")
        record = logs.records[0]
        self.assertEqual(record.fields, {"tenant_id": str(TENANT_A), "sqlstate": "42501"})  # type: ignore[attr-defined]
        self.assertNotIn("secret-row-content", JsonFormatter().format(record))

    def backend_pid(self) -> int:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT pg_backend_pid()")
            return int(cursor.fetchone()[0])


@tag("integration")
class AuditTests(TenantIsolationTestCase):
    tenant_tables = ("audit.tenant_event", "audit.platform_event", "presence_core_rlsfixtureparent")

    def event(self, tenant: UUID | None = TENANT_A, **fields: Any) -> AuditEvent:
        return AuditEvent(
            **{"action": "test.event", "result": "success", "actor": "service:tests", **fields}, tenant_id=tenant
        )

    def stored(self, table: str, tenant: UUID | None = None) -> list[dict[str, Any]]:
        """Rows as the owner role sees them (FORCE RLS: tenant rows need the tenant's context)."""
        context = tenant_context(tenant, using="migrator") if tenant else transaction.atomic(using="migrator")
        with context, connections["migrator"].cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table} ORDER BY occurred_at")
            names = [c.name for c in cursor.description]
            return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]

    def test_tenant_event_is_stored_redacted_and_correlated(self) -> None:
        with correlate(request_id="req-1", trace_id="t" * 32), tenant_context(TENANT_A):
            event_id = append_audit(
                self.event(target=SEEDED_TEXT, detail={"password": SEEDED_SECRETS["password"], "note": SEEDED_TEXT})
            )
        (row,) = self.stored("audit.tenant_event", TENANT_A)
        self.assertEqual((row["id"], row["tenant_id"], row["request_id"]), (event_id, TENANT_A, "req-1"))
        self.assertEqual(json.loads(row["detail"])["password"], REDACTED)  # Django reads jsonb as text
        assert_clean(self, json.dumps(row, default=str))

    def test_platform_event_has_no_tenant(self) -> None:
        with transaction.atomic():
            append_audit(self.event(tenant=None, actor="operator:op-1", break_glass_reason="incident 7"))
        (row,) = self.stored("audit.platform_event")
        self.assertEqual((row["actor"], row["break_glass_reason"]), ("operator:op-1", "incident 7"))
        self.assertNotIn("tenant_id", row)

    def test_runtime_role_cannot_change_or_delete_audit_rows(self) -> None:
        with tenant_context(TENANT_A):
            append_audit(self.event())
        with transaction.atomic():
            append_audit(self.event(tenant=None))
        statements = {
            "update tenant": "UPDATE audit.tenant_event SET result = 'failure'",
            "delete tenant": "DELETE FROM audit.tenant_event",
            "truncate tenant": "TRUNCATE audit.tenant_event",
            "update platform": "UPDATE audit.platform_event SET result = 'failure'",
            "delete platform": "DELETE FROM audit.platform_event",
            "read platform": "SELECT count(*) FROM audit.platform_event",
        }
        for name, sql in statements.items():
            with self.subTest(name), self.assertRaises(DatabaseError), tenant_context(TENANT_A):
                with connections["default"].cursor() as cursor:
                    cursor.execute(sql)
        self.assertEqual([r["result"] for r in self.stored("audit.tenant_event", TENANT_A)], ["success"])
        self.assertEqual([r["result"] for r in self.stored("audit.platform_event")], ["success"])

    def test_tenant_reads_and_writes_only_its_own_audit_rows(self) -> None:
        with tenant_context(TENANT_A):
            append_audit(self.event(TENANT_A))
        with tenant_context(TENANT_B):
            append_audit(self.event(TENANT_B))
        with tenant_context(TENANT_A), connections["default"].cursor() as cursor:
            cursor.execute("SELECT tenant_id FROM audit.tenant_event")
            self.assertEqual(cursor.fetchall(), [(TENANT_A,)])
        with self.assertRaises(DatabaseError), tenant_context(TENANT_A):
            append_audit(self.event(TENANT_B))
        with connections["default"].cursor() as cursor:  # no tenant context sees nothing
            cursor.execute("SELECT count(*) FROM audit.tenant_event")
            self.assertEqual(cursor.fetchone(), (0,))

    def test_failed_audit_write_rolls_back_the_operation(self) -> None:
        with self.assertLogs("presence.audit", level="ERROR") as logs, self.assertRaises(DatabaseError):
            with tenant_context(TENANT_A):
                RlsFixtureParent.objects.create(tenant_id=TENANT_A, name="must-not-commit")
                append_audit(self.event(TENANT_B))  # rejected by RLS
        self.assertEqual(logs.records[0].getMessage(), "audit_write_failed")
        with tenant_context(TENANT_A):
            self.assertFalse(RlsFixtureParent.objects.exists())

    def test_append_outside_a_transaction_is_refused(self) -> None:
        with self.assertRaises(RuntimeError):
            append_audit(self.event(tenant=None))
