# ADR-0029 — Production Tenant AI Auth Is Separate from Development Harness Auth
Status: Accepted; narrowed by ADR-0030 (2026-11-14). Subscription credentials stay barred from unattended and client-triggered work, and are permitted for operator-started or approved runs through an official harness on the Worker VM.

## Decision
Developer harness OAuth/subscription credentials are not a production tenant AI architecture. Production uses explicit provider API/contract credentials or local inference through the AI Capability Gateway.
