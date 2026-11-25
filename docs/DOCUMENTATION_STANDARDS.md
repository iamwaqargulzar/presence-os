# Documentation Standards

Current as of 2026-11-25. These rules apply to every document in this repository.

## 1. Document types and where they live

| Type | Purpose | Location | Changes |
|---|---|---|---|
| Entry points | First files to open | `README.md` (people), `00_START_HERE.md` (agents), `AGENTS.md` (rules) | Kept current |
| Status and handoff | Where work stands; session handoffs | `docs/handoff/` | See [handoff protocol](handoff/README.md) |
| Task contract | One implementable task, with acceptance tests | `specs/R<n>/R<n>-NNN-<slug>.md` | Revised with a revision note |
| ADR | One architectural decision and why | `docs/adrs/ADR-NNNN-<slug>.md` | Immutable once accepted; changed only by a new ADR that supersedes it |
| Decision Register | One-line index of all locked decisions | `docs/DECISION_REGISTER.md` | Kept current |
| Open questions | Everything not yet decided | `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | Item moves to "Decided" when settled |
| Focused document | How one subsystem works | `docs/<area>/<topic>.md` | Kept current |
| Runbook | Step-by-step operations procedure | `docs/runbooks/` | Tested before relied on |
| Research note | Dated survey; reference only, never authority | `docs/research/<TOPIC>_YYYY-MM-DD.md` | Not updated; a new note replaces it |
| Evidence | Proof that work was done and checked | `evidence/` | Never edited; see [evidence/README.md](../evidence/README.md) |
| Contract schema | Machine-checked interface | `contracts/schemas/*.schema.json` | Changed only with the task or ADR that needs it |
| Template | Starting point for the types above | `templates/` | Kept current |
| Archive | No longer current | `docs/archive/` | Never edited; never cited as current |
| Compiled copy | Generated reading copies | `docs/MASTER_SPEC.md`, `docs/COMPLETE_CONTEXT_EXPORT.md`, `docs/INDEX.md` | Generated only; never edited by hand |

`docs/<area>` is one of: `adrs`, `ai`, `architecture`, `compliance`, `data`, `delivery`, `domains`, `handoff`, `infrastructure`, `integrations`, `operations`, `product`, `research`, `runbooks`, `security`, `ux`. Add a new area only when at least three documents need it.

## 2. Authority
The authority order in [`AGENTS.md`](../AGENTS.md) decides conflicts. A document never silently overrides a higher one; a real conflict becomes an ADR or a task note.

## 3. Every document
- Starts with one `# Title` line.
- Says how current it is: a line such as `Current as of 2026-11-25.` near the top, or a revision note for task contracts and a status line for ADRs.
- Uses absolute dates in `YYYY-MM-DD`. Never "today", "recently" or "next week".
- Links other files with relative Markdown links, so `tools/build_docs.py` can check them.
- Names vendors, versions, prices and platform rules as dated facts that must be rechecked before use.
- Contains no secrets, tokens, personal email addresses or client personal data.

## 4. Writing style
- Plain, short sentences. The owner reads English as a second language.
- One idea per paragraph. Lists and tables for anything with more than three items.
- Say what is not decided or not checked. Do not hide gaps.
- Use "must" for rules, "should" for strong defaults, "may" for options.
- Define a term once in [`GLOSSARY.md`](GLOSSARY.md); then use it the same way everywhere.

## 5. Names
- Files: `kebab-case.md` for focused documents; `UPPER_SNAKE_CASE.md` for repository-wide documents; dated research and audit files end in `_YYYY-MM-DD.md`.
- Identifiers: ADR-NNNN (four digits), R<n>-NNN for tasks, E-NNN for edge cases. Numbers are never reused.

## 6. ADR lifecycle
`Proposed` → `Accepted` → (`Superseded by ADR-NNNN` | `Deprecated`). Use [`templates/ADR_TEMPLATE.md`](../templates/ADR_TEMPLATE.md). Every accepted ADR gets a line in the Decision Register and a `CHANGELOG.md` entry.

## 7. Change procedure
1. Edit the source document, never a compiled copy.
2. Record decisions in the Decision Register or an ADR, and remove them from the open-questions list.
3. Add a dated line to `CHANGELOG.md` for any durable change.
4. Run `python3 tools/build_docs.py`; it must print `links: ok`.
5. Commit with a Conventional Commit message (see [`CONTRIBUTING.md`](../CONTRIBUTING.md)).

## 8. Archive
Move a document to `docs/archive/` when it stops being current. Do not delete it, and update every link that pointed to it. Nothing under `docs/archive/` is current.
