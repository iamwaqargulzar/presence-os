# Evidence

Durable proof that work was done and checked. Nothing here is a plan; plans live in `specs/`.

## Layout
```
evidence/
  <release>/<task-id>/report.md      implementation report (templates/IMPLEMENTATION_REPORT_TEMPLATE.md)
  <release>/<task-id>/review.md      independent review, required for security-critical tasks
  <release>/exit-audit.md            release exit audit (R0-010, R1-010, …)
  restore-drills/YYYY-MM-DD.md       backup restore drill records
  benchmarks/                        harness and model benchmark records
```
Example: `evidence/R0/R0-001/report.md`.

## Rules
- Written when a task passes its gates, in the same commit or pull request as the work.
- Never edited afterwards. A correction is a new dated file that links the old one.
- No secrets, tokens, personal data or raw model transcripts. Link to stored artifacts instead.
- Files dated before 2026-11-25 (for example `HARNESS_TELEMETRY_AND_FLASH_BENCHMARK_2026-08-08.md`) stay where they are.
