# Tenant Lifecycle

> **Updated 2026-11-14** for [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md): Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.

A tenant is one of the operator's own companies or one managed client. Tenants are created by the operator; there is no signup, trial or payment state.

States:
- PROVISIONING
- ACTIVE
- PAUSED
- OFFBOARDING
- CLOSED
- DELETION_PENDING
- DELETED

Transitions affect:
- client sign-in;
- Action Broker;
- scheduled workflows;
- domains;
- connections;
- budgets;
- retention.

PAUSED blocks new external actions and new AI work while preserving data.

OFFBOARDING is a controlled workflow: export for the client, disconnect external accounts, release or transfer domains, then retention and deletion with legal-hold considerations.

When a tenant is created, the operator's `MANAGED_SERVICE` access grant for that tenant is created and audited at the same time.
