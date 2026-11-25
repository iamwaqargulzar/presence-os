# ADR-0034 — R0-001 Tooling Choices and Node Without Corepack
Status: Accepted (2026-11-25). Made during R0-001 under the owner's delegation in ADR-0032.

## Context
ADR-0032 chose pnpm "enabled through Corepack". On 2026-11-25 the newest Node LTS is 26.13.1, and Node 26 no longer ships Corepack (its documentation page for v26 returns 404; v24 still has it). R0-001 also had to choose the lint, format and test tools, which no ADR named.

## Decision
1. **Node and pnpm pinning.** `apps/web/package.json` pins pnpm in `packageManager` and Node in `devEngines.runtime` (`onFail: download`). pnpm downloads both exact versions itself. Corepack is not required. This replaces only the Corepack sentence of ADR-0032 section 3.
2. **Release cooldown.** pnpm's `minimumReleaseAge` default (one day) stays on. A package newer than that is not pinned; the previous release is used. An exception needs a written reason in the pull request.
3. **Python gates:** ruff (format and lint) and mypy in strict mode with django-stubs.
4. **Web gates:** Biome (format and lint, recommended preset, Next and React domains, which include accessibility rules) and `tsc --noEmit`. ESLint and Prettier are not used: one tool instead of three, with a much smaller dependency tree.
5. **Tests:** Django's test runner and the standard-library `unittest` for Python; `node:test` for the web smoke test. No pytest or Vitest yet. Both can be added later; existing tests still run under them.
6. **Secret scan:** gitleaks from its official container image, pinned by digest, run by `make scan-secrets` and by the pre-commit hook. **Dependency scan:** the package managers' own `uv audit` and `pnpm audit`.
7. **No database in R0-001.** PostgreSQL 18 and its driver arrive in R0-003 together with the non-owner runtime role. The psycopg driver is LGPL-3.0 and needs the review note required by ADR-0033 section 3 at that point.

## Alternatives considered
- Keep Corepack by installing it separately: an extra tool for something pnpm now does itself.
- ESLint with `eslint-config-next` and Prettier: the Next.js default, but three tools and a much larger dependency tree.
- pytest with pytest-django: familiar, but two more dependencies that R0-001 does not need.

## Consequences
- `uv audit` is marked experimental by uv on 2026-11-25; its output format may change.
- Biome's Next.js rules are fewer than `eslint-config-next`'s. Revisit if a missed rule causes a defect.
- The gate command contract (Makefile targets) does not depend on these tools; a tool can be swapped without breaking R0-002 or R0-011.

## Security impact
The cooldown lowers the risk of installing a just-published malicious release. The secret scanner runs from a digest-pinned image, so the hook cannot silently change.

## Cost/operational impact
None. All tools are free and run locally.

## Migration / rollback
Revert the commit. No data is involved.

## Supersedes
ADR-0032 section 3, the Corepack sentence only.

## Superseded by
