# Service Levels and SLOs

Do not promise enterprise uptime from a single primary Presence host.

Before external SLAs:
- measure availability;
- prove restore;
- define RPO/RTO;
- identify single points of failure;
- establish incident process;
- establish maintenance policy.

Internal SLO candidates should cover:
- control-plane availability;
- Action Broker success/latency;
- workflow task age;
- domain/certificate health;
- connection health;
- voice latency;
- backup freshness;
- restore success;
- cross-tenant security = zero tolerance.
