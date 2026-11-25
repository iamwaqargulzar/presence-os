# Environments and Release Boundaries

Minimum:
- local/development
- test/CI
- staging
- production

Later:
- canary

## Separation

- distinct secrets/credentials;
- distinct databases;
- production data not copied casually into dev;
- sandbox outbound controls;
- no production tokens in coding agent environments.

## Release channels

- DEV
- STAGING
- CANARY
- STABLE

Feature flags:
- OFF
- INTERNAL
- BETA
- SELECTED_CLIENTS
- ALL

Schema changes must support controlled rollout and rollback/forward-fix.
