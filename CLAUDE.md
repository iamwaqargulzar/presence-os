# Claude Code instructions

@AGENTS.md

## Start of every session
1. Read `docs/handoff/STATUS.md`. It says where work stands and what to do next.
2. Open only the task contract it names and the documents that contract links.
3. Never read `docs/COMPLETE_CONTEXT_EXPORT.md` or `docs/MASTER_SPEC.md` whole; search them instead.

## End of a session, or when it gets long
Follow `docs/handoff/README.md`: record decisions, write a handoff log entry, overwrite `STATUS.md`, run `python3 tools/build_docs.py`, then tell the operator a new session can start.

## Ponytail plugin
Use ponytail (`/ponytail`, `/ponytail-review`) to keep code small. It never removes what this project requires: gates, tenant-isolation and authorization tests, dependency reviews, implementation reports, documentation updates and handoffs. Where ponytail and `AGENTS.md` disagree, `AGENTS.md` wins.
