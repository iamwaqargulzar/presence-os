#!/bin/sh
# Proves each gate fails on a seeded violation (R0-001 negative checks).
# It only creates new files named *seed*, and removes them on exit; it never edits tracked files.
set -u
cd "$(dirname "$0")/.."
SEEDS=""
cleanup() { for f in $SEEDS; do git rm -q --cached --ignore-unmatch "$f" >/dev/null 2>&1; rm -f "$f"; done; }
trap cleanup EXIT INT TERM
failures=0

expect_fail() { # <gate> <file> <content>
  SEEDS="$SEEDS $2"
  printf '%s\n' "$3" > "$2"
  if make -s "$1" >/dev/null 2>&1; then echo "FAIL: '$1' passed with seeded $2"; failures=$((failures + 1))
  else echo "ok:   '$1' rejects $2"; fi
  rm -f "$2"
}

expect_fail fmt-check apps/core/presence_core/seed_fmt.py 'x=1'
expect_fail fmt-check apps/web/app/seed_fmt.ts 'export const x={a:1}'
expect_fail lint apps/core/presence_core/seed_lint.py 'import os'
expect_fail lint apps/web/app/seed_lint.tsx 'export const X = () => <img src="/a.png" />;'
expect_fail typecheck apps/core/presence_core/seed_type.py 'def f() -> int:
    return "x"'
expect_fail typecheck apps/web/app/seed_type.ts 'export const n: number = "x";'
expect_fail test apps/core/presence_core/test_seed.py 'import unittest


class Seed(unittest.TestCase):
    def test_fails(self) -> None:
        self.fail("seeded")'
expect_fail test contracts/schemas/seed.schema.json '{"$schema": "https://json-schema.org/draft/2020-12/schema", "type": 5}'
expect_fail test-integration apps/core/presence_core/migrations/0001_seed_broken.py 'from django.db import migrations


class Migration(migrations.Migration):
    operations = [migrations.RunSQL("THIS IS NOT SQL")]'

# A known-vulnerable dependency (Django 4.2.0 has published advisories), audited by the same tool as `make audit`.
seed_dir="$(mktemp -d)"
printf '# /// script\n# dependencies = ["django==4.2.0"]\n# ///\n' > "$seed_dir/seed_vulnerable.py"
if uv audit --preview-features audit-command --script "$seed_dir/seed_vulnerable.py" >/dev/null 2>&1; then
  echo "FAIL: dependency audit passed a known-vulnerable package"; failures=$((failures + 1))
else echo "ok:   dependency audit rejects a known-vulnerable package"; fi
rm -rf "$seed_dir"

# A credential-shaped value built at run time, so this script itself holds no key pattern.
fake="ghp_$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 36)"
SEEDS="$SEEDS seed_credential.txt"
printf 'token = "%s"\n' "$fake" > seed_credential.txt
git add -f seed_credential.txt
if make -s scan-staged >/dev/null 2>&1; then echo "FAIL: secret hook passed a seeded credential"; failures=$((failures + 1))
else echo "ok:   'scan-staged' (pre-commit hook) rejects a seeded credential"; fi

[ "$failures" -eq 0 ] && echo "gate self-test: all gates reject seeded violations"
exit "$failures"
