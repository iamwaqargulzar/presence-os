# Secrets Management

Bring a proper secrets boundary in before public beta with real customer integrations.

Recommended: OpenBao or equivalent.

## Requirements

- namespace/separate tenant and platform secrets;
- least-privilege policies;
- audit;
- rotation where supported;
- revocation/expiry;
- short-lived capabilities/tokens when possible;
- never expose raw secrets to model context;
- never log bearer tokens/passwords;
- do not scatter encrypted credential columns throughout application modules.

## Secrets Broker

Application modules request a capability/reference, not direct database secret material wherever practical.

Production coding agents and untrusted workers have no production secret access.
