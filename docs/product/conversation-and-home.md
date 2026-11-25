# Conversation Shell and Agent Home


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## Experience goal

Once an authenticated administrator or tenant user enters Presence OS, default landing is the **Agent Home**.

The page should not overwhelm with modules. It should answer:
- What needs attention?
- What improved?
- What opportunities are new?
- What has Presence completed?
- What can I ask/do now?

## Agent Home information model

Primary:
- voice-reactive Presence visualization;
- conversational input/transcript;
- concise synthesis such as “There are two things worth your attention.”

Supporting areas:
- Important / urgent items
- Opportunities
- Recent improvements
- Recent progress
- optional compact health/score indicators

Avoid dashboard-card overload.

## Voice embodiment

The agent does **not need a face**. Preferred direction is an expressive, abstract, voice-reactive kinetic form:
- idle breathing/subtle motion;
- listening contraction/focus;
- speaking deformation/equalizer response;
- thinking/progress state;
- accessible non-motion equivalent.

The form should feel like a crafted instrument/sculptural interface, not a generic glowing AI orb.

## Visual direction — not locked

UI is deliberately editable later. Current constraints:
- avoid stereotypical “AI slop”;
- no default neon blue/purple gradients;
- avoid excessive glow/glassmorphism;
- avoid huge rounded SaaS cards;
- tighter radii, flatter surfaces, strong typography;
- neutral/dark or light themes with a limited accent;
- editorial/asymmetric composition is welcome;
- motion should communicate state, not decorate.

Do not block R0/R1 architecture on final visual design.

## Natural language behavior

Users may speak unfinished thoughts, change direction, use pronouns/references and resume context later.

Conversation state should track:
- active_profile
- active_page
- selected_entity
- last_artifact
- current_preview
- active_task
- recent_references

High-confidence referent: proceed.
Low-confidence referent: ask one short clarification.

## Initiative

Configurable:
- asked-only
- important
- proactive

Communication:
- concise
- balanced
- detailed

Progressive disclosure is default.
