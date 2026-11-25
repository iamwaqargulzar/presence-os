# Network and Service Exposure

## Public surface

Initial: Cloudflare Tunnel to Edge Gateway. No inbound public ports required.

Never publicly expose:
- Proxmox UI/SSH;
- PostgreSQL;
- Redis;
- Temporal;
- OpenBao;
- Docker API;
- ComfyUI;
- llama.cpp;
- voice-model ports;
- worker debug ports.

## Internal access

Inference is reached over private LAN/VLAN from authorized Presence services.

Prefer internal DNS names over hard-coded LAN IPs.

## Static-IP future mode

If/when switched to direct origin:
- Edge Gateway is the public target, not Proxmox;
- default-deny host firewall;
- forward/expose only required port(s), preferably 443;
- SSH management from LAN/VPN only;
- restrict origin to Cloudflare where practical;
- preserve Cloudflare-origin authentication controls;
- same downstream Edge routing.

Router “DMZ host” forwarding all ports increases the importance of host firewalling and is not a substitute for explicit port forwarding.


## Direct-origin hardening options

If static direct origin is activated:
- allowlist Cloudflare origin source ranges and block other Internet sources where practical;
- use Full (strict) origin TLS where feasible;
- enable Cloudflare Authenticated Origin Pulls (mTLS) as an additional origin-authentication layer;
- prefer zone-level/per-hostname AOP with an account-controlled certificate if stricter provenance is needed;
- keep SSH off the public Internet (LAN/VPN/secure management path only).

These controls are additive; a simple default-deny host firewall remains mandatory.
