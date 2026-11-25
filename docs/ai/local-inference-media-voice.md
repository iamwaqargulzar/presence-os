# Local Inference, Media and Voice

## Inference host

Hardware:
- Ryzen 7 8700G
- 32 GB RAM
- RTX 3090

Services:
- llama.cpp
- ComfyUI
- voice stack
- video model on demand

## Normal loading

Keep commonly used image + voice services available where resource budget permits.

Video is not default; load on demand because of VRAM/resource pressure.

## Voice baseline

Previously selected implementation direction:
- faster-whisper primary STT
- Qwen3-ASR 0.6B secondary, 1.7B on demand
- Chatterbox Multilingual V3 primary local TTS
- optional Chatterbox Turbo for low-latency English
- Qwen3-TTS not the current primary recommendation

These are replaceable implementation candidates, not permanent architecture.

Cloud fallbacks may include suitable commercial STT/TTS/realtime voice providers when policy/cost allows.

## Gateway

Do not expose model ports publicly. A private Voice/Inference Gateway owns:
- stable API;
- queue/resource policy;
- model load/unload;
- tenant/task attribution;
- latency/usage metrics;
- fallbacks.
