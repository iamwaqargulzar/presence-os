# Session Handoff Protocol

Current as of 2026-11-25. Applies to every working session, by a person or an AI agent.

## Why
A session has limited memory. When it gets long it becomes slow and expensive, and it may be compacted, which loses detail. A handoff writes down what the next session needs, so it can start small and correct instead of re-reading everything.

## The three handoff files

| File | What it holds | Size rule | Changed when |
|---|---|---|---|
| [`STATUS.md`](STATUS.md) | Where the whole project stands now: phase, current task, next step, blockers, owner decisions waiting. | At most about 80 lines. Overwritten, never appended. | At every handoff and when a task finishes. |
| `log/YYYY-MM-DD-<slug>.md` | One session's handoff: what was done, what was decided, what is unfinished, exact next step. | At most about 120 lines. | Once, at the end of a session that changed anything important. Never edited later. |
| Implementation report in `evidence/` | The record of one finished task (see [`evidence/README.md`](../../evidence/README.md)). | Template fields only. | When a task passes its gates. |

Decisions never live only in a handoff. A decision goes into the Decision Register, an ADR or the task contract first; the handoff links to it.

## When to hand off
Hand off at a natural break (between steps, never in the middle of one) when any of these is true:
- the task is finished, and the next task is a different one;
- the session has been compacted once already;
- the session holds many long tool outputs, screenshots or large file reads;
- the work moves to a different release, subsystem or repository;
- the operator asks for it.

Mid-task, when the history still matters, compacting the session is the cheaper choice. Write `STATUS.md` first anyway, so nothing is lost if compaction drops detail.

## How to hand off (closing session)
1. Record every decision made in this session in its proper place (Decision Register, ADR, task contract, open-questions list).
2. Write `log/YYYY-MM-DD-<slug>.md` from [`templates/SESSION_HANDOFF_TEMPLATE.md`](../../templates/SESSION_HANDOFF_TEMPLATE.md).
3. Overwrite `STATUS.md` so it is true now. Link the new log entry.
4. Add a line to `CHANGELOG.md` if anything durable changed.
5. Run `python3 tools/build_docs.py`; it must print `links: ok`.
6. Commit with a message such as `docs(handoff): <slug>` when the operator has asked for commits.
7. Tell the operator in one line that the handoff is written and a new session can start.

## How to start (new session)
Read only this, in order, and stop when you have enough:
1. `AGENTS.md` (loaded automatically through `CLAUDE.md` for Claude Code).
2. [`STATUS.md`](STATUS.md).
3. The newest file in `log/`, only if `STATUS.md` points to unfinished work in it.
4. The task contract named in `STATUS.md`, and only the documents and ADRs it links.

Do **not** read `docs/COMPLETE_CONTEXT_EXPORT.md` (about 800 KB) or `docs/MASTER_SPEC.md` (about 110 KB) whole. They are compiled copies for disaster recovery and offline reading. Search them, or open the focused source file instead.

Check that `STATUS.md` matches the repository (`git log -5`, `git status`). If it does not, say so before working.

## Rules
- Plain short sentences. Absolute dates (`2026-11-25`), never "today" or "last week".
- No secrets, tokens, personal email addresses or client personal data in any handoff file.
- A handoff states facts and links; it does not repeat whole documents.
- Say what was not checked or not finished. A handoff that hides a gap is worse than none.
