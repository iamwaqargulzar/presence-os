#!/bin/sh
# Create or update the two Django database roles (R0-003, docs/security/database-tenancy-rls.md).
# Idempotent. Runs inside the postgres container as the bootstrap superuser, which Django never uses:
#   docker compose exec -T -e PRESENCE_DB_MIGRATOR_PASSWORD -e PRESENCE_DB_APP_PASSWORD postgres sh -s < infra/postgres/roles.sh
set -eu
: "${PRESENCE_DB_MIGRATOR_PASSWORD:?set it in .env}" "${PRESENCE_DB_APP_PASSWORD:?set it in .env}"
psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
\getenv migrator_pw PRESENCE_DB_MIGRATOR_PASSWORD
\getenv app_pw PRESENCE_DB_APP_PASSWORD
SELECT 'CREATE ROLE presence_migrator' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'presence_migrator') \gexec
SELECT 'CREATE ROLE presence_app' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'presence_app') \gexec
-- Migration role: owns the schema. CREATEDB only so Django can create test databases; never grant it in production.
ALTER ROLE presence_migrator LOGIN CREATEDB NOSUPERUSER NOCREATEROLE NOBYPASSRLS PASSWORD :'migrator_pw';
-- Runtime role: owns nothing and never bypasses row-level security.
ALTER ROLE presence_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT PASSWORD :'app_pw';
ALTER DATABASE :"DBNAME" OWNER TO presence_migrator;
SQL
