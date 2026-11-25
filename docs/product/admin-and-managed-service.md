# Operator and Managed-Service Experience

> **Updated 2026-11-14** for [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md): Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.

## Operator console

The console is mobile-first, on its own control-plane hostname, with Google sign-in only. From a phone the operator can:
- ask for a task in plain language;
- schedule recurring tasks;
- read reports;
- approve or reject drafts and actions;
- start or approve runs that use the operator's subscription;
- deploy or modify a property;
- see cost per client.

Agent Home may synthesize:
- tenant incidents;
- reauthentication requirements;
- failing workflows;
- provider/API degradation and subscription rate limits reached;
- cost anomalies and budget thresholds;
- backup/restore health;
- pending releases;
- ecosystem/API changes.

## Acting on a client's tenant

- show "Acting as Managed Operator" clearly;
- show tenant context persistently;
- enforce the TenantAccessGrant;
- audit authority source and reason;
- the client can see the access.

## Client request and approval queue

A client request never runs anything by itself. It lands in the operator's queue. Where a tenant requires it, a draft waits for the Client Approver before it is published. An approval covers only the exact artifact shown.

## Maintenance agent

A future Platform Engineer/Ecosystem Watch may detect external API changes, diagnose adapter breakage, create a tested patch and ask the operator for release approval. It never self-approves production changes.

## AI policy administration
The operator maps task classes to versioned model profiles, sets a per-tenant override and provider policy, inspects the effective resolution, and changes a default with preview and rollback. Tenant overrides are preserved.

The Platform/Admin AI has separate platform configuration and does not become a tenant's Presence AI or inherit tenant business authority.
