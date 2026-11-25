# Internal Networking and Inference Reachability

Cloudflare solves public Internet → Edge. It does not replace LAN networking.

The Presence Core reaches the inference server over private LAN/VLAN.

Prefer:
`http(s)://inference.presence.internal:<gateway-port>`
over hard-coded addresses.

A DHCP reservation/static private address may back that hostname.

## Inference boundary

Do not expose raw:
- llama.cpp;
- ComfyUI;
- STT/TTS model servers.

Expose a private stable **Inference/Voice Gateway** to authorized Presence services.

The gateway provides:
- authentication;
- tenant/task correlation;
- queueing;
- model routing;
- usage/cost telemetry;
- resource governance;
- stable APIs despite model changes.

## Firewall concept

Allow:
- authorized Presence service → inference gateway
- management network → SSH/management

Deny arbitrary LAN/Internet clients and block inference server access to management/control networks unless explicitly required.
