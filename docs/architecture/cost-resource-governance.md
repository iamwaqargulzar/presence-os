# Cost and Resource Governance

## Cost Governor

Controls:
- model tier/reasoning;
- tokens;
- tool calls;
- media operations;
- provider selection;
- retries;
- workflow max cost;
- tenant/service-wallet limits.

Every operation must be attributable by:
- tenant/profile;
- task/workflow/action;
- provider/model;
- tokens including cached tokens;
- tool/media/external cost.

### Reserve then settle

For concurrent expensive actions:
1. reserve budget;
2. execute;
3. settle actual cost;
4. refund unused reservation.

This prevents race conditions where several workers all pass a pre-check.

### Circuit breakers

Stop loops by thresholds on:
- steps;
- turns;
- retries;
- time;
- cost;
- repeated identical failures.

## Resource Governor

Separate from money.

Controls:
- tenant concurrency;
- LLM concurrency;
- GPU queue;
- browser concurrency;
- crawl concurrency;
- media queue;
- background priority;
- provider rate limits.

Weighted fair scheduling prevents noisy neighbors.

Suggested priority:
1. realtime voice
2. interactive user request
3. tenant foreground
4. normal scheduled work
5. internal scans
6. video/background
