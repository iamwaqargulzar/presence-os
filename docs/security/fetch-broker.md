# Fetch Broker / SSRF Boundary

Agents and skills do not raw-fetch arbitrary URLs.

Fetch Broker policy:
- HTTP(S) only by default;
- resolve DNS before connection and re-resolve after redirects;
- block localhost/loopback;
- block RFC1918/private networks;
- block link-local;
- block cloud metadata endpoints;
- block Proxmox/control/GPU/home LAN;
- block file://, gopher:// and unexpected schemes;
- enforce redirect count;
- enforce response size/time/type limits;
- optionally allow-list destinations for high-risk tools;
- log destination and policy result.

Protect against DNS rebinding and redirect-to-private-network attacks.

Tenant-supplied URLs are not inherently trusted.
