# ADR-0022 — Stable Tenant AI Identity Separate from Model
Status: Accepted

## Decision
Each tenant/profile has one logical Presence AI identity. Model/provider/reasoning is a versioned AIModelProfile and can change without changing tenant memory/authority identity.
