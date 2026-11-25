# Consent, Communication Preferences and Suppression

Communication compliance is shared infrastructure.

Entities:
- ConsentRecord
- SuppressionRecord
- CommunicationPreference
- Jurisdiction
- Source
- Timestamp
- Evidence

`DO_NOT_CONTACT` overrides agent recommendations.

Maintain proof where channel policy requires active opt-in (for example WhatsApp use cases).

Email/SMS/WhatsApp/voice workflows must consult suppression and jurisdiction policy immediately before sending, including delayed/scheduled actions.

Do genuine personalization; do not turn Presence into a mass-spam engine.
