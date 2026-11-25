# apps/web
Next.js and strict TypeScript control-plane frontend. UI logic must respect Agent Home, accessibility, explicit profile context and authorization semantics.

Current as of 2026-11-25 (R0-001): a placeholder page only, to prove the app starts.
- `proxy.ts` sets an `x-request-id` header and logs one JSON line per request.
- No environment value is exposed to the browser. Only `NEXT_PUBLIC_` variables would be, and none exist.
- Node and pnpm versions are pinned in `package.json` (`devEngines`, `packageManager`); see ADR-0034.

Run with `make dev-web`; test with `make test`. Setup: [developer bootstrap](../../docs/runbooks/developer-bootstrap.md).
