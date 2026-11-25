# Tenant Limits, Budgets and Usage

> **Updated 2026-11-14** for [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md): Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.

The file name is kept so existing links work. There are no plans, subscriptions, seats, invoices or payment processing in Presence OS.

## Purpose

The operator pays for everything the system does. This area exists to keep that spending bounded and visible per client.

## Tenant limits

A limit is a versioned record the operator sets per tenant:
- key (for example active properties, runs per day, posts per day, custom domains, storage);
- limit value and period;
- revision, so a change never rewrites history.

The limit check answers `(tenant, key, quantity) → allow/deny + reason` and fails closed.

## Budgets

- **Tenant budget:** a money cap per tenant and period.
- **Global budget:** a money cap across all tenants per period, with an alert threshold below the cap.

Both are checked. A reservation that would exceed either is denied.

## Reserve then settle

1. Estimate.
2. Reserve atomically against the tenant and global budgets, with a price snapshot.
3. Execute.
4. Settle the actual amount.
5. Refund the unused reserve.

No expensive operation runs on a pre-check alone. A reservation expires if its worker dies.

## Usage ledger

Append-only. Records platform actions, AI usage (raw tokens and money cost, with provenance grade) and external services. Every record is attributable to tenant, task/workflow/action and provider/model.

## Subscription-backed work

Runs on the operator's own AI subscriptions have no per-call money cost. They are still recorded in the ledger with token usage where the harness reports it, and they count against run limits. The subscription's own rate limit is treated as a capacity limit, not as budget.

## Tenant operating state

The operator can pause a tenant. A paused tenant blocks new work through the Action Broker and keeps its data.

## Cost report

A per-tenant report for a period is produced from the ledger alone. If the operator charges clients, that happens outside Presence OS and this report is the input.

## Client view

A client can read their own tenant's usage summary. A client cannot change limits or budgets.
