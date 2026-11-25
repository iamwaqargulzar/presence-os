import json
import logging

from django.core.management import call_command
from django.db import DatabaseError, connections, transaction
from django.test import SimpleTestCase, tag

from presence_core.models import RlsFixtureChild, RlsFixtureParent
from presence_core.observability import JsonFormatter
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
