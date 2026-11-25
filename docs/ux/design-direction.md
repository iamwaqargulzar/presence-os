# UI / Visual Design Direction

The final interface is intentionally not locked before engineering foundation.

## Experience invariants

- Agent Home after login for admin and tenant.
- Voice/text conversation is central.
- Attention, opportunities, improvements and progress are immediately understandable.
- Avoid overwhelm and module-dashboard density.
- Important actions have clear consequence/authorization states.
- Accessible with motion disabled.

## Aesthetic constraints from current exploration

Avoid:
- neon blue/purple “AI” gradients;
- excessive glow;
- glassmorphism;
- giant rounded cards;
- generic futuristic SaaS dashboard;
- decorative waveform clichés everywhere.

Prefer:
- mature product/editorial feel;
- strong typography;
- flatter surfaces;
- tighter radii;
- asymmetry/negative space where useful;
- restrained dark and light themes;
- limited accent palette;
- subtle material/3D treatment;
- motion tied to system/voice state.

The voice-reactive form can be visually expressive; the surrounding OS should remain calm.

## Design-system implementation rule

Build semantic tokens/components, not hard-coded aesthetics:
- color roles
- spacing
- typography
- radius
- elevation
- motion
- focus
- status priority.

This allows redesign without rewriting product logic.
