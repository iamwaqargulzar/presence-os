"""Reusable tenant-isolation test case (R0-003). Every new tenant table gets a test built on it.

Queries run as the runtime role (`default`, presence_app). Seeding and cleanup use the migration role, which
owns the tables; FORCE RLS means seeding still needs a tenant context.
"""

from collections.abc import Callable
from typing import Any
from uuid import UUID

from django.db import DatabaseError, connections, models
from django.test import SimpleTestCase

from presence_core.tenancy import tenant_context

TENANT_A = UUID("00000000-0000-4000-8000-00000000000a")
TENANT_B = UUID("00000000-0000-4000-8000-00000000000b")


class TenantIsolationTestCase(SimpleTestCase):
    # Not TestCase: rows must be committed so each tenant_context() is a real transaction, as in production.
    databases = {"default", "migrator"}
    tenant_tables: tuple[str, ...] = ()  # truncated after each test

    def tearDown(self) -> None:
        if self.tenant_tables:
            with connections["migrator"].cursor() as cursor:
                cursor.execute(f"TRUNCATE {', '.join(self.tenant_tables)} CASCADE")
        super().tearDown()

    @classmethod
    def tearDownClass(cls) -> None:
        # The test runner closes only the migration alias before dropping the test database.
        connections["default"].close()
        super().tearDownClass()

    def seed[M: models.Model](self, tenant: UUID, model: type[M], **fields: Any) -> M:
        with tenant_context(tenant, using="migrator"):
            return model._default_manager.using("migrator").create(tenant_id=tenant, **fields)

    def assert_crud_isolated(self, model: type[models.Model], make_fields: Callable[[UUID], dict[str, Any]]) -> None:
        """Tenant A can read and write only its own rows of `model`; no tenant context sees and writes nothing."""
        own = self.seed(TENANT_A, model, **make_fields(TENANT_A))
        other = self.seed(TENANT_B, model, **make_fields(TENANT_B))
        objects = model._default_manager.using("default")

        with tenant_context(TENANT_A):
            with self.subTest("select"):
                self.assertEqual(list(objects.values_list("pk", flat=True)), [own.pk])
                self.assertFalse(objects.filter(pk=other.pk).exists())
            with self.subTest("update"):
                self.assertEqual(objects.filter(pk=other.pk).update(tenant_id=TENANT_A), 0)
            with self.subTest("delete"):
                self.assertEqual(objects.filter(pk=other.pk).delete()[0], 0)
        with self.subTest("insert into other tenant"):
            with self.assertRaises(DatabaseError), tenant_context(TENANT_A):
                objects.create(tenant_id=TENANT_B, **make_fields(TENANT_B))
        with self.subTest("move own row to other tenant"):
            with self.assertRaises(DatabaseError), tenant_context(TENANT_A):
                objects.filter(pk=own.pk).update(tenant_id=TENANT_B)
        with self.subTest("no context fails closed"):
            self.assertEqual(objects.count(), 0)
            self.assertEqual(objects.all().delete()[0], 0)
            with self.assertRaises(DatabaseError):
                objects.create(tenant_id=TENANT_A, **make_fields(TENANT_A))

        with tenant_context(TENANT_B):
            self.assertTrue(objects.filter(pk=other.pk, tenant_id=TENANT_B).exists(), "other tenant's row changed")
