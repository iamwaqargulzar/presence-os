import json
import logging

from django.db import connection
from django.test import SimpleTestCase, TestCase, tag

from presence_core.observability import JsonFormatter


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
class DatabaseTests(TestCase):
    def test_migrations_ran_from_empty_on_the_test_database(self) -> None:
        self.assertTrue(connection.settings_dict["NAME"].startswith("test_"))
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM django_migrations WHERE app = 'contenttypes'")
            (applied,) = cursor.fetchone()
        self.assertGreater(applied, 0)
