# Delegation, Managed Service and Break Glass

## Managed mode

Every tenant is managed by the operator (ADR-0030). There is no self-service mode. Clients sign in with limited roles: viewer, requester or approver.

## TenantAccessGrant

Fields:
- tenant
- grantee user/organization
- role
- permissions
- approval categories
- valid_from
- valid_until
- granted_by
- status
- reason (MANAGED_SERVICE / SUPPORT / TEMPORARY / CONTRACTOR)

The client can inspect the operator's access but cannot revoke or pause it. The operator ends service from the operator console when the client asks (owner decision, 2026-11-15). A client can always disconnect their own connected accounts.

## Platform vs tenant authority

A single person may simultaneously be:
- Platform Owner
- delegated Managed Operator

These are distinct authorities and must be shown/audited distinctly.

## Break Glass

Emergency access:
- explicit reason required;
- short-lived;
- least scope;
- highly visible audit;
- internal notification;
- periodic review.

It is not a convenient super-admin mode.

Some actions remain tenant-owner-only or require stronger confirmation:
- ownership transfer;
- tenant deletion;
- removing tenant owner;
- critical security settings;
- legal/financial commitments.
