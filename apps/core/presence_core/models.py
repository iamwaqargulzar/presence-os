import uuid

from django.db import models


# Fixture tables that prove the tenant pattern (R0-003); real entities arrive with R0-004.
class RlsFixtureParent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    name = models.CharField(max_length=50)

    class Meta:
        # Target of the composite (tenant_id, id) foreign key from children.
        constraints = [models.UniqueConstraint(fields=["tenant_id", "id"], name="rlsfixtureparent_tenant_id")]

    def __str__(self) -> str:
        return self.name


class RlsFixtureChild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    # The real constraint is the composite foreign key in migration 0001, so a child can only point at a
    # parent of its own tenant and the check cannot reveal another tenant's rows.
    parent = models.ForeignKey(RlsFixtureParent, on_delete=models.CASCADE, db_constraint=False)
    note = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.note
