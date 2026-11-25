# Vanity Hostname Policy

## Eligibility

- the operator assigns vanity hostnames; they are not sold;
- the number per tenant is a tenant limit.

## Syntax

Recommended initial policy:
- ASCII lowercase letters, digits, hyphen;
- 3–32 chars;
- no leading/trailing hyphen;
- no confusing Unicode/homograph names.

Internationalized customer-owned domains can be supported separately with explicit IDN/Punycode safety handling.

## Reserved/protected names

Reserve infrastructure/system names such as:
admin, api, app, auth, billing, cdn, docs, help, login, mail, portal, preview, status, support, www.

Also detect high-risk impersonation patterns and obvious protected-brand abuse.

Do not depend on a static giant trademark list alone.

## Downgrade

If vanity is no longer included:
- grace period;
- continue serving;
- the operator decides retention or release;
- do not suddenly break a shared URL.

## Cancellation/release

Do not immediately recycle a previously public vanity hostname.

State:
ACTIVE → RELEASE_PENDING → QUARANTINED → AVAILABLE

Initial quarantine may be ~90 days or longer based on policy/risk; exact period is a product/legal decision.

Some heavily used/high-risk names may require manual release.
