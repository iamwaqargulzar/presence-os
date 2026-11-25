# ADR-0024 — Pin Effective Model Profile Per Run/Session
Status: Accepted

## Decision
Resolve platform/package/tenant/run policy at run start and pin the AIModelProfile revision. Mid-run admin changes apply only at safe boundaries or checkpoint/stop.
