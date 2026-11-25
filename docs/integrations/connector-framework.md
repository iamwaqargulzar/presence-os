# Connector Framework

A connector adapts Presence capabilities to an external system/provider.

## Connector contract

Each connector declares:
- provider/system;
- authentication types;
- capabilities;
- scopes;
- rate-limit handling;
- idempotency behavior;
- webhook support;
- data sensitivity;
- policy limitations;
- health check;
- version/deprecation metadata.

## Provider adapters

External API changes should be localized to versioned adapters.

The ecosystem watcher can detect change and create tasks, but production connector changes pass normal test/release gates.

## Capability matrix

Maintain a current matrix by provider:
- supported action;
- API vs browser;
- permissions/scopes;
- restrictions;
- policy status;
- fallback;
- last verified date.
