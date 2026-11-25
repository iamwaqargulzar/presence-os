# Context Compiler and Memory Loading

## Goal

Never send the entire historical conversation merely because it exists.

Memory levels:
- L0 recent conversation/task context
- L1 rolling summary
- L2 durable preferences/decisions
- L3 tenant knowledge
- L4 workflow/task state
- L5 immutable/raw archive

Normal model context uses L0 plus relevant L1–L4. L5 is fetched only when needed.

## Prompt order

Keep stable material first:
1. Presence system policy
2. tool/skill contracts
3. authorization
4. tenant-stable context
5. task-stable context
6. retrieval
7. recent messages
8. current request

This improves both relevance and provider prompt caching.

## Cache key inputs

Include where relevant:
- tenant/profile;
- skill version;
- tool version;
- input hash;
- permission context;
- provider/model;
- data/knowledge version.

Invalidate on:
- access revocation;
- permission downgrade;
- tenant deletion;
- knowledge supersession;
- privacy request;
- credential revocation.

Redis is acceleration, not durable truth.
