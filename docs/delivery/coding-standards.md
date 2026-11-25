# Coding Standards

## General

- clear names;
- small coherent modules;
- explicit types/contracts;
- no hidden cross-module side effects;
- structured errors;
- UTC storage with explicit user timezone rendering;
- migrations in version control;
- deterministic IDs where appropriate, secure randomness where required;
- dependency minimization.

## Python/Django

- type annotations on public/service boundaries;
- service/domain layer for important operations;
- transactions around invariants;
- avoid business logic in serializers/views only;
- tenant context explicit;
- security-sensitive queries tested under runtime DB role.

## TypeScript/Next.js

- strict TypeScript;
- server/client boundary explicit;
- accessible semantic components;
- do not expose secrets through client bundles;
- generated API types/contracts where useful.

## API

- versionable;
- idempotency for side effects;
- machine-readable errors;
- request/trace IDs;
- pagination;
- rate/entitlement enforcement;
- no direct database IDs as authorization.

## Documentation

Code comments explain why/invariants, not obvious syntax.
Update ADR/docs/task when behavior or architecture changes.
