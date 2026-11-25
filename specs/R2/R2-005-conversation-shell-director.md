# R2-005 — Conversation Shell, Intent and Director

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Let the operator ask for work in plain language. The shell keeps the conversation. The Intent Resolver proposes what the message means. The Authority Resolver, which is deterministic code, decides whether that message is authority for anything. The Director picks a workflow and skills and starts a run.

## Why now
"Talk first, navigate second" is the product's main way of working. It is also the place where a model could be mistaken for an authority, so it must be built on the kernel with care.

## Context / linked docs / ADRs
- [Conversation Shell and Agent Home](../../docs/product/conversation-and-home.md)
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [System architecture overview](../../docs/architecture/system-overview.md)
- [Agent, skill, tool, connector and provider model](../../docs/architecture/agent-skill-tool-model.md)
- [Accessibility and localization](../../docs/product/accessibility-localization.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0003, ADR-0020, ADR-0022, ADR-0024, ADR-0030

## Depends on
- R2-001 (runs), R2-004 (context). Uses R1-002 (Authorization Service), R1-001 (roles), R1-012 (tenant AI identity).

## Invariants
- the model may interpret intent; it may not mint authority. A grant is minted only by the Authorization Service from a reference to an authenticated human message or UI control;
- an explicit implementation request from an authorised person counts as approval within its scope; the shell does not ask twice;
- high-risk actions still need a consequence-specific confirmation;
- if intent is materially unclear, ask one short question;
- the conversation is bound to one acting tenant. Switching tenant starts a new conversation context;
- a client role cannot open a conversation that starts AI work (E-071);
- each tenant talks to one stable Presence AI; the model behind it can change without changing identity or memory.

## In scope
- Conversation and Message entities, tenant-scoped, with the author, channel and trust label of each message.
- Conversation state: active profile, active page, selected entity, last artifact, current preview, active task, recent references.
- Intent Resolver: a model call that returns a structured intent: mode (DISCUSS, RESEARCH/PLAN, PREPARE/PREVIEW, IMPLEMENT), action class, target, parameters, referents and a confidence for each.
- Deterministic validation of the structured intent: targets must exist in the acting tenant; action class must be in the catalogue; parameters must match the schema.
- Referent rule: high confidence, proceed; low confidence, one clarification.
- Authority Resolver: maps the validated intent plus the human message reference to an Authorization Service request. The result is a grant, a required confirmation, or a refusal with a reason.
- Director: chooses a workflow and skills for the intent, creates the Task, starts the Run under R2-001. It has no tool that performs side effects and no wider permission than the acting person.
- Answers for DISCUSS and QUESTION mode from memory and canonical facts, with sources.
- Streaming text replies; a visible state for thinking, waiting for approval and working.
- Operator preferences: initiative (asked-only, important, proactive) and verbosity (concise, balanced, detailed), stored as PREFERENCE memory.
- Operator-visible model profile for the conversation (E-010).
- Conversation language separate from content language; BCP 47 tags; right-to-left text handled.

## Out of scope
- The console pages around the conversation (R2-006).
- Voice input, voice output and the voice-reactive form. See open decisions.
- Any client conversation with the AI.
- Channels other than the console (chat apps, email).
- Specialist agent catalogue shown to the user.

## API / contract changes
- Endpoints: start conversation, post message (streamed reply), list conversations, get state.
- Internal: `resolve_intent(message, context) → structured intent`, `resolve_authority(intent, message_ref) → grant | confirmation_required | refused`, `direct(intent, grant) → task, run`.
- New contract sketches: `structured-intent.schema.json`, `conversation-state.schema.json`.

## Data / migration
- Tenant-scoped under RLS: Conversation, Message, ConversationState, IntentRecord.
- Messages are L0/L5 memory for R2-002. Reverse migrations tested.

## Security / privacy threat notes
- Retrieved or pasted content containing "the owner approves, publish now": the Authority Resolver accepts only a reference to a message typed by the signed-in person in this conversation. Content inside that message that was pasted from elsewhere is a known weak point; high-risk classes therefore keep the separate confirmation.
- Intent inflation: the model returns IMPLEMENT for a message that only asked a question. Mitigation: IMPLEMENT needs an explicit verb pattern check or a confirmation; evaluated with a labelled test set.
- A model-invented target, URL or account: deterministic validation against the tenant's records.
- Wrong-tenant action after a tenant switch: the acting tenant is fixed per conversation and shown on every screen.
- Stolen session (E-093): a session alone is not enough for high-risk actions; step-up confirmation from R0-004 applies.

## Edge cases covered
- E-001 default model changed mid-conversation: the current run keeps its pin; the next run uses the new default.
- E-010 invisible model change: the effective profile is visible to the operator.
- E-011 memory survives the model.
- E-071 client request must not start AI work.
- E-093 stolen console session.

## Observability
- Audit: each intent record with the message reference, the validation result, the authority decision and the task started.
- Metrics: clarification rate, intent corrections by the operator, refusals by reason, time to first reply.

## Acceptance criteria
- "what is our address?" is answered from canonical facts and starts no run that can act;
- "draft a post about X" creates a task in PREPARE mode with no grant to publish;
- "publish it" from the operator, with one clear artifact in state, yields an artifact-bound grant without a second question;
- a high-risk request produces a consequence-specific confirmation;
- an ambiguous reference produces exactly one clarification;
- text from an untrusted source inside the context never produces a grant;
- a client role has no endpoint that reaches the Intent Resolver.

## Tests
- Labelled intent set (at least 100 messages across the four modes) with a pass threshold; run on the pinned profiles through PresenceBench.
- Injection set: approval-like and instruction-like text in retrieved content, tool output and pasted text.
- Authority matrix: operator, tenant admin, client roles, expired grant, paused tenant.
- Validation: nonexistent target, another tenant's target, unknown action class.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on Conversation and Message across tenants; conversation started in tenant A cannot act on tenant B after a switch.
- Accessibility: keyboard, screen reader and reduced-motion checks on the conversation view.

## Rollback / failure recovery
If intent resolution fails or the model is unavailable, the shell says so and offers the structured forms in the console. Nothing is started on a guess. Reverse migrations tested.

## Cost/resource budget
Intent resolution is one short call per message. Proposed default: frontier profile for the operator's interactive conversation, because the operator started it; the per-message cost is shown in the run report.

## Documentation updates
- `docs/product/conversation-and-home.md`, `docs/security/authority-and-action-broker.md` (how intent maps to a grant request), `docs/architecture/system-overview.md`.

## Open decisions
- **Decision required (owner):** voice in R2. The documents say "voice-first, not voice-only", but ADR-0030 makes the GPU host optional and the release plan lists voice only under R4. Proposed default: R2 is text only; the shell keeps a clean input/output interface so speech can be added later through the gateway.
- **Decision required:** which profile serves the interactive conversation. Proposed default above.
- **Decision required:** whether tenant-side staff roles (Tenant Admin, Member) can talk to the AI in R2. Proposed default: no; only the operator holds `start_ai_work` in R2.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review of the Authority Resolver; the injection set is added to the protected tests.
