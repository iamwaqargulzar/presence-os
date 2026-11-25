# OAuth, Connections and Browser Identity

## Preferred connection order

1. OAuth/API through client's own browser.
2. Managed persistent browser profile if API is unavailable/inadequate and permitted.
3. Human/manual takeover for challenges.

Clients enter credentials/OTP themselves. Presence should avoid storing passwords.

## OAuth

Follow current browser/OAuth security BCP:
- Authorization Code + PKCE;
- exact redirect URIs;
- state/CSRF protections;
- least scopes;
- secure refresh-token storage;
- rotation/revocation handling;
- provider-specific reauthentication.

## Connection states

- CONNECTED
- DEGRADED
- REAUTH_REQUIRED
- PERMISSION_LOST
- RATE_LIMITED
- PROVIDER_OUTAGE
- POLICY_BLOCKED
- DISCONNECTED

Connection records include:
Provider, Account, CredentialRef, Scopes, Status, ExpiresAt, RefreshState, LastVerified, Health, Capabilities.

## Browser identity states

- authenticated
- healthy
- challenge
- reauth
- revoked
- expired

Never bypass CAPTCHA, rate limits, anti-bot systems or platform restrictions. Pause and request human takeover when required.
