# AI Capability Gateway


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## Stable interface

Application code requests capabilities through an AI Capability Gateway rather than calling model vendors directly.

Representative operations:
- reason()
- generate_text()
- code()
- image()
- video()
- embed()
- rerank()
- vision()
- stt()
- tts()
- realtime_voice()

## Provider routing modes

- LOCAL_FIRST
- CLOUD_FIRST
- CLOUD_ONLY
- LOCAL_ONLY
- SMART / AUTO

Tenant privacy/policy may forbid cloud use.

## Routing inputs

- required capability;
- quality threshold;
- latency;
- cost;
- tenant/provider policy;
- data sensitivity;
- current availability/rate limits;
- model qualification;
- context size;
- language;
- media requirements.

Local inference is an optimization and privacy option, not a hard dependency.
