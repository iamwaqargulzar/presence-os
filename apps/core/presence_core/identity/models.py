"""Person, tenant, profile, membership and invitation (R0-004, docs/product/person-profile-tenant-model.md).

A Person is one human, identified by a Google account subject (allauth's SocialAccount.uid), never by email.
Every other table here is a tenant table under row-level security (migration 0001).
"""

import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class Person(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # Contact address from Google, not an identity: not unique, never used to match a login.
    email = models.EmailField(blank=True)
    display_name = models.CharField(max_length=200, blank=True)
    # Platform operator (ADR-0030). Grants creating tenants only; tenant data still needs a membership.
    is_operator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "id"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = BaseUserManager["Person"]()

    class Meta:
        # Sign-in is Google only: the database refuses any usable password hash ("!" marks an unusable one).
        constraints = [models.CheckConstraint(condition=models.Q(password__startswith="!"), name="person_no_password")]

    def set_password(self, raw_password: str | None) -> None:
        raise ValueError("Presence OS has no password sign-in (ADR-0039)")

    def __str__(self) -> str:
        return str(self.id)


class TenantState(models.TextChoices):
    PROVISIONING = "PROVISIONING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    OFFBOARDING = "OFFBOARDING"
    CLOSED = "CLOSED"
    DELETION_PENDING = "DELETION_PENDING"
    DELETED = "DELETED"


# docs/operations/tenant-lifecycle.md. R0 performs PROVISIONING -> ACTIVE; the rest are defined for later tasks.
TENANT_TRANSITIONS: dict[str, frozenset[str]] = {
    TenantState.PROVISIONING: frozenset({TenantState.ACTIVE, TenantState.CLOSED}),
    TenantState.ACTIVE: frozenset({TenantState.PAUSED, TenantState.OFFBOARDING}),
    TenantState.PAUSED: frozenset({TenantState.ACTIVE, TenantState.OFFBOARDING}),
    TenantState.OFFBOARDING: frozenset({TenantState.ACTIVE, TenantState.CLOSED}),
    TenantState.CLOSED: frozenset({TenantState.DELETION_PENDING}),
    TenantState.DELETION_PENDING: frozenset({TenantState.CLOSED, TenantState.DELETED}),
    TenantState.DELETED: frozenset(),
}


class Tenant(models.Model):
    # The primary key is named tenant_id so the standard RLS policy applies to the tenant row itself.
    tenant_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=20, choices=TenantState.choices, default=TenantState.PROVISIONING)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def transition(self, new_state: str) -> None:
        """Move to `new_state` if the lifecycle allows it; the caller saves."""
        if new_state not in TENANT_TRANSITIONS[self.state]:
            raise ValidationError(f"tenant cannot move from {self.state} to {new_state}")
        self.state = new_state
        self.version += 1

    def __str__(self) -> str:
        return self.name


class ProfileKind(models.TextChoices):
    INDIVIDUAL = "INDIVIDUAL"  # a person's own profile; it is its own tenant
    COMPANY = "COMPANY"


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    kind = models.CharField(max_length=20, choices=ProfileKind.choices)
    name = models.CharField(max_length=200)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["tenant", "id"], name="profile_tenant_id")]

    def __str__(self) -> str:
        return self.name


class Role(models.TextChoices):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    CLIENT_VIEWER = "CLIENT_VIEWER"
    CLIENT_REQUESTER = "CLIENT_REQUESTER"
    CLIENT_APPROVER = "CLIENT_APPROVER"
    CONTRACTOR = "CONTRACTOR"


MANAGING_ROLES = frozenset({Role.OWNER, Role.ADMIN})


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    # Composite (tenant_id, profile_id) key in migration 0001: the profile must be in the same tenant.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, db_constraint=False)
    role = models.CharField(max_length=20, choices=Role.choices)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["person", "profile"], name="membership_person_profile")]

    def __str__(self) -> str:
        return f"{self.person_id} {self.role} {self.profile_id}"


class Invitation(models.Model):
    """The only way in: a Google sign-in whose verified email matches a pending invitation becomes a member."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, db_constraint=False)  # composite key, as above
    email = models.EmailField()  # stored lower-case
    role = models.CharField(max_length=20, choices=Role.choices)
    grants_operator = models.BooleanField(default=False)  # only bootstrap_operator sets it
    accepted_by = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL)
    accepted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"invitation {self.id}"
