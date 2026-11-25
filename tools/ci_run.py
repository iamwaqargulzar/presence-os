#!/usr/bin/env python3
"""Run the CI stages in order and write reports/ci-result.json (CI result contract, R0-002).

Standard library only, so it runs before any dependency is installed.
Schema: contracts/schemas/ci-result.schema.json. Exit code 0 only if every stage passed or was skipped.
"""

import datetime
import fnmatch
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
PROTECTED_FILE = ROOT / ".github" / "protected-paths"
SECRET_NAME = re.compile(r"SECRET|PASSWORD|TOKEN|KEY", re.IGNORECASE)

STAGES: list[tuple[str, list[str]]] = [
    ("static", ["make", "-s", "fmt-check", "lint", "typecheck"]),
    ("unit", ["make", "-s", "test"]),
    ("integration", ["make", "-s", "test-integration"]),
    ("security", ["make", "-s", "audit", "scan-secrets"]),
    ("protected-paths", [sys.executable, "tools/ci_run.py", "protected-paths"]),
    ("gate-selftest", ["tools/gate_selftest.sh"]),
]


def redact(text: str, env: dict[str, str]) -> str:
    """Replace the value of every credential-like environment variable before a log is stored."""
    for name, value in env.items():
        if SECRET_NAME.search(name) and len(value) >= 8:
            text = text.replace(value, "[REDACTED]")
    return text


def protected_changes(changed: list[str], patterns: list[str]) -> list[str]:
    return [f for f in changed if any(fnmatch.fnmatch(f, p) for p in patterns)]


def read_patterns() -> list[str]:
    lines = PROTECTED_FILE.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def check_protected_paths() -> int:
    """Fail a pull request that changes a protected path unless the owner added the approval label."""
    base = os.environ.get("PRESENCE_CI_BASE_SHA", "")
    if not base:
        print("not a pull request: nothing to compare")
        return 0
    if not re.fullmatch(r"[0-9a-f]{40}", base):
        print(f"FAIL: PRESENCE_CI_BASE_SHA is not a commit hash: {base!r}")
        return 1
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    hits = protected_changes(diff.stdout.split(), read_patterns())
    for f in hits:
        print(f"protected path changed: {f}")
    if hits and os.environ.get("PRESENCE_CI_PROTECTED_APPROVED") != "true":
        print("FAIL: add the label 'owner-approved-protected-change' after the owner has reviewed these files")
        return 1
    return 0


def git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def run_stage(name: str, command: list[str], env: dict[str, str]) -> dict[str, object]:
    print(f"::group::stage {name}: {' '.join(command)}", flush=True)
    start = time.monotonic()
    proc = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output = redact(proc.stdout, env)
    print(output, flush=True)
    print("::endgroup::", flush=True)
    log = REPORTS / f"{name}.log"
    log.write_text(output, encoding="utf-8")
    return {
        "name": name,
        "command": " ".join(command),
        "status": "passed" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "duration_s": round(time.monotonic() - start, 1),
        "log": str(log.relative_to(ROOT)),
    }


def main() -> int:
    if sys.argv[1:] == ["protected-paths"]:
        return check_protected_paths()
    REPORTS.mkdir(exist_ok=True)
    env = dict(os.environ)
    started = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    stages = [run_stage(name, cmd, env) for name, cmd in STAGES]
    result = {
        "schema_version": 1,
        "commit": git_sha(),
        "started_at": started,
        "run_url": env.get("PRESENCE_CI_RUN_URL", ""),
        "status": "passed" if all(s["status"] == "passed" for s in stages) else "failed",
        "stages": stages,
    }
    (REPORTS / "ci-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for s in stages:
        print(f"{s['status']:>7}  {s['name']} (exit {s['exit_code']}, {s['duration_s']}s)")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
