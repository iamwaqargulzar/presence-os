# Client Onboarding and Time-to-Value

> **Updated 2026-11-14** for [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md): Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.

There is no public signup and no trial. The operator onboards each client.

## Flow

1. The operator creates the tenant and sets its limits, budget and provider policy.
2. Minimal profile input by the operator, text or voice.
3. Presence researches permitted public information.
4. Build the Presence Snapshot.
5. Present what is known, uncertain and missing.
6. The operator invites the client (Google sign-in) with a role: viewer, requester or approver.
7. The client connects their external accounts on each platform's own consent page. Connections are optional and do not block basic value.
8. Produce a prioritized first 30-day plan.
9. Create initial work or a preview where applicable.
10. Show the client what is done, what is proposed and what needs their approval.

Target: the operator sees meaningful work within roughly 10–15 minutes of creating the tenant, without being blocked by DNS or optional integrations.

## Platform-hosted route

Every property gets an immediate random platform hostname. Work can be viewed and shared before a custom domain is connected.

## What the client sees

- before/after;
- evidence-backed work completed;
- drafts waiting for approval;
- their connections, with the ability to disconnect.
