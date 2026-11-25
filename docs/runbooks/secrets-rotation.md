# Runbook — Secrets Rotation

For each credential:
1. identify owner/provider/tenant;
2. identify dependent services;
3. create new credential with least scope;
4. store through Secrets Broker/OpenBao;
5. deploy reference/version;
6. verify service;
7. revoke old credential;
8. verify no fallback to old credential;
9. audit;
10. update rotation metadata.

Emergency compromise:
- revoke first where impact permits;
- pause affected actions;
- rotate;
- validate audit and external account activity.
