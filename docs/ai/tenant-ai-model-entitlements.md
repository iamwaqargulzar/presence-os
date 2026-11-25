# Tenant Presence AI, Model Profiles and Provider Policy

> **Updated 2026-11-14** for [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md): Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.

The file name is kept so existing links work. Package entitlements, AI tiers sold in plans, entitlement exceptions and AI Compute Units no longer exist.

## Stable identity

Each tenant has one stable logical Presence AI (`TenantAIIdentity`). Memory, authority and identity never live in the model. Models are replaceable behind it.

## Model profiles

An `AIModelProfile` is a versioned record: provider, model, capabilities, privacy class, credential class, price reference, fallback list, status (DRAFT, ACTIVE, DEPRECATED, DISABLED). Model names are data, never code.

## Credential class

- `OPERATOR_SUBSCRIPTION`: the operator's own subscription, used only through the provider's official harness on the Worker VM, and only for a run the operator started or approved.
- `API`: pay-per-use provider credentials through the AI Capability Gateway. Required for scheduled and unattended runs.

A client request never starts a run. It creates a queue item for the operator.

## Task-class routing

The platform default is chosen by task class:
- planning, architecture, security-sensitive work and review → frontier profile;
- high-volume, low-risk, machine-checkable work → low-cost API profile.

The mapping is configuration and is changed through a versioned `ModelPolicyRevision` (see [model default change procedure](../operations/model-policy-change-management.md)).

## Tenant configuration

`TenantAIConfiguration` has two modes:
- PLATFORM_DEFAULT: follow the task-class routing;
- PINNED: use a named profile.

## Tenant provider policy

Per tenant, the operator records which providers and regions may receive which data classes. It is a hard filter in resolution and in fallback. A provider the policy excludes is never used for that tenant, for any task class.

## Resolution

Order: authorised run override → tenant override → platform default.

The result is a pinned profile revision plus a human-readable reason, or "paused" with a reason. Resolution fails closed.

## Pinning

The effective profile revision is pinned for a run or session. A default change applies at the next boundary, never mid-run.

## Fallback

A fallback candidate must pass the provider policy, privacy class, required capabilities, budget reservation, credential class and provider health. If none passes, the run checkpoints and pauses.

## Local inference

Routing is CLOUD_ONLY by default. The private GPU host is optional and may be off. A request that needs a local-only profile while the host is off pauses with a reason.

## Usage

Raw tokens (input, cache write, cache read, output, reasoning) and money cost are recorded per run with a provenance grade. Unavailable values are recorded as unavailable, never as zero.

## Platform Admin AI

Has its own configuration, no tenant memory and no inherited tenant authority.
