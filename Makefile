# Gate command contract (R0-001). CI (R0-002) and the gate runner (R0-011) call these targets.
# Exit code 0 = pass, non-zero = fail. Renaming a target or changing its meaning is a breaking change.
.PHONY: bootstrap fmt fmt-check lint typecheck test test-integration check audit scan-secrets scan-staged \
	services-up services-down dev-core dev-web

# Local settings (.env, never committed); CI sets the same variables itself.
-include .env
export $(shell sed -n 's/^\([A-Z_]*\)=.*/\1/p' .env 2>/dev/null)

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
	$(TEST_ENV) uv run mypy apps/core contracts tools/ci_run.py tools/tests
	$(WEB) typecheck

test:
	$(TEST_ENV) uv run python apps/core/manage.py test presence_core --exclude-tag integration
	uv run python -m unittest discover -s contracts/tests
	uv run python -m unittest discover -s tools/tests
	$(WEB) build
	$(WEB) test

check: fmt-check lint typecheck test

# Needs Docker. Django creates the test database, migrates it from empty, and drops it afterwards.
test-integration: services-up
	$(TEST_ENV) uv run python apps/core/manage.py makemigrations --check --dry-run
	$(TEST_ENV) uv run python apps/core/manage.py test presence_core --tag integration --noinput

services-up:
	docker compose up -d --wait postgres

services-down:
	docker compose down

audit:
	uv audit --locked --preview-features audit-command
	$(WEB) audit --audit-level high

scan-secrets:
	$(GITLEAKS) git --redact /repo

scan-staged:
	$(GITLEAKS) git --pre-commit --staged --redact /repo

dev-core:
	uv run python apps/core/manage.py runserver 127.0.0.1:8000

dev-web:
	$(WEB) dev
