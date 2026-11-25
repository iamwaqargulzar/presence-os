# ADR-0006 — Cloudflare Tunnel First, Static-Origin Ready
Status: Accepted

## Decision
Use Cloudflare Tunnel as initial/default ingress.

## Constraint
Keep Edge Gateway/internal routing unchanged so a later static-public-IP direct origin is an infrastructure migration only. Maintain tested forward and rollback runbooks.
