# Accessibility and Localization

## Accessibility target

WCAG 2.2 AA baseline.

Voice-first must never mean voice-only.

Required:
- keyboard navigation;
- semantic structure;
- screen-reader support;
- captions and streaming transcript;
- clear listening state;
- barge-in/interruption;
- visible confirmations for consequential actions;
- focus visibility;
- target-size requirements;
- reduced motion;
- contrast;
- accessible authentication;
- no drag-only interaction;
- redundant-input avoidance.

Testing must include automated checks plus manual keyboard, NVDA/VoiceOver and RTL testing.

## User preferences

- voice + text
- voice mostly
- text mostly
- text only
- speech speed
- response verbosity
- initiative level
- reduced motion
- simplified mode

## Localization architecture

Separate:
- conversation language;
- content language;
- locale;
- timezone;
- currency.

Use:
- Unicode;
- CLDR;
- BCP 47 language tags.

Support code-switching and transliteration.

Launch priority favors broadly spoken international languages such as English, Spanish, Mandarin Chinese, Hindi, Arabic, French, Portuguese, Japanese and German. Urdu is desirable and architecture-supported but is not a launch blocker.

Preserve original-language evidence. Support RTL structurally from the beginning.
