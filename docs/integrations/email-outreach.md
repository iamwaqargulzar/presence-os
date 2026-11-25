# Email and Outreach Infrastructure

Separate Presence transactional/platform mail from tenant marketing/cold outreach to protect sender reputation.

Potentially isolate high-risk tenants further.

## Deliverability agent

Monitor:
- SPF
- DKIM
- DMARC
- alignment
- bounce
- complaint
- unsubscribe
- sending volume
- reputation signals.

## Sending policy

Every send checks:
- authorization;
- entitlement/wallet;
- recipient consent/suppression;
- jurisdiction;
- channel/provider policy;
- volume/rate limits;
- exact artifact/destination.

Avoid generic mass AI spam. Prefer evidence-based, genuinely personalized outreach.


## Dated Gmail deliverability reference

At the August 2026 baseline, Google's sender guidelines state:
- all senders to personal Gmail need SPF or DKIM, valid DNS/PTR, TLS and compliant formatting;
- senders over about 5,000 messages/day to Gmail accounts need SPF + DKIM + DMARC/alignment and one-click unsubscribe for marketing/subscribed mail;
- Google says keep spam rate below 0.3%, and its FAQ recommends below 0.1% and avoiding 0.3% or higher.

References:
- https://support.google.com/mail/answer/81126
- https://support.google.com/mail/answer/14229414

Treat thresholds/policies as time-sensitive; the deliverability policy matrix must revalidate them.
