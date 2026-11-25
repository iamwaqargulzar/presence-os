# Gate command contract (R0-001). CI (R0-002) and the gate runner (R0-011) call these targets.
# Exit code 0 = pass, non-zero = fail. Renaming a target or changing its meaning is a breaking change.
.PHONY: bootstrap fmt fmt-check lint typecheck test check audit scan-secrets scan-staged dev-core dev-web

GITLEAKS_IMAGE := ghcr.io/gitleaks/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f
GITLEAKS := docker run --rm -v "$(CURDIR):/repo" -w /repo $(GITLEAKS_IMAGE)
# Not a secret: settings need a key to import; tests and type checks never use it for anything.
TEST_ENV := PRESENCE_SECRET_KEY=insecure-test-only
WEB := cd apps/web && pnpm -s

bootstrap:
	uv sync --locked
	$(WEB) install --frozen-lockfile
	git config core.hooksPath .githooks

fmt:
	uv run ruff format .
	$(WEB) fmt

fmt-check:
	uv run ruff format --check .
	$(WEB) fmt-check

lint:
	uv run ruff check .
	$(WEB) lint

typecheck:
	$(TEST_ENV) uv run mypy apps/core contracts
	$(WEB) typecheck

test:
	$(TEST_ENV) uv run python apps/core/manage.py test presence_core
	uv run python -m unittest discover -s contracts/tests
	$(WEB) build
	$(WEB) test

check: fmt-check lint typecheck test

audit:
	uv audit --locked --preview-features audit-command
	$(WEB) audit --audit-level high

scan-secrets:
	$(GITLEAKS) git --redact /repo

scan-staged:
	$(GITLEAKS) git --pre-commit --staged --redact /repo

dev-core:
	set -a && . ./.env && set +a && uv run python apps/core/manage.py runserver 127.0.0.1:8000

dev-web:
	$(WEB) dev
