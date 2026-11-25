import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import ci_run  # noqa: E402


class RedactTests(unittest.TestCase):
    def test_credential_values_are_removed(self) -> None:
        env = {"PRESENCE_DB_PASSWORD": "s3cret-value-123", "HOME": "/home/runner"}
        out = ci_run.redact("password=s3cret-value-123 home=/home/runner", env)
        self.assertEqual(out, "password=[REDACTED] home=/home/runner")

    def test_short_values_are_left_alone(self) -> None:
        self.assertEqual(ci_run.redact("a 1 b", {"API_KEY": "1"}), "a 1 b")


class ProtectedPathTests(unittest.TestCase):
    def test_matches_ci_config_and_specs_only(self) -> None:
        changed = [".github/workflows/ci.yml", "specs/R0/R0-001.md", "Makefile", "apps/core/x.py"]
        hits = ci_run.protected_changes(changed, ci_run.read_patterns())
        self.assertEqual(hits, changed[:3])

    def test_protects_its_own_list_and_runner(self) -> None:
        own = [".github/protected-paths", "tools/ci_run.py", "tools/gate_selftest.sh"]
        self.assertEqual(ci_run.protected_changes(own, ci_run.read_patterns()), own)


class ResultContractTests(unittest.TestCase):
    def test_stage_record_matches_schema(self) -> None:
        schema = json.loads((ROOT / "contracts/schemas/ci-result.schema.json").read_text())
        stage = {"name": "x", "command": "true", "status": "passed", "exit_code": 0, "duration_s": 0.1, "log": "x"}
        result = {
            "schema_version": 1,
            "commit": "0" * 40,
            "started_at": "2026-11-25T00:00:00+00:00",
            "run_url": "",
            "status": "passed",
            "stages": [stage],
        }
        Draft202012Validator(schema).validate(result)


class WorkflowPolicyTests(unittest.TestCase):
    """Environment separation rules that can be checked mechanically (environments.md)."""

    def setUp(self) -> None:
        files = (ROOT / ".github/workflows").glob("*.yml")
        code = ["\n".join(ln for ln in p.read_text().splitlines() if not ln.lstrip().startswith("#")) for p in files]
        self.workflows = code

    def test_ci_uses_no_repository_secrets(self) -> None:
        for text in self.workflows:
            self.assertNotIn("secrets.", text)

    def test_ci_never_runs_untrusted_code_with_write_access(self) -> None:
        for text in self.workflows:
            self.assertNotIn("pull_request_target", text)
            self.assertIn("permissions:\n  contents: read", text)

    def test_actions_are_pinned_by_commit(self) -> None:
        for text in self.workflows:
            for line in text.splitlines():
                if "uses:" in line:
                    self.assertRegex(line, r"@[0-9a-f]{40}")


if __name__ == "__main__":
    unittest.main()
