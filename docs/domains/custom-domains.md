# Customer Custom Domains

Custom domains are optional and do not block onboarding.

Lifecycle:
1. tenant enters domain;
2. validate ownership/routing requirements;
3. guide automatic provider OAuth/Domain Connect where possible;
4. provide manual CNAME/TXT fallback;
5. validate hostname;
6. validate certificate;
7. attach to service;
8. health-check;
9. optionally promote to primary;
10. retain random canonical platform route.

Prefer keeping the customer's existing DNS provider.

If DNS migration is necessary:
- preflight all records;
- preserve MX/SPF/DKIM/DMARC and other critical records;
- use rollback plan.

Customer keeps domain ownership.
