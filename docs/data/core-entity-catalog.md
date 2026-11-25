# Core Entity Catalog

This is a conceptual catalog, not the final ORM schema.

Identity/control:
- Person
- Tenant
- Profile
- Membership
- Role
- Permission
- TenantAccessGrant
- AuthorizationGrant

Knowledge:
- Fact
- Evidence
- Observation
- CandidateFact
- FactConflict
- MemoryItem
- SourceSnapshot

Work:
- Goal
- Task
- Workflow
- Artifact
- Approval
- Action
- ActionAttempt
- AttentionItem
- Opportunity

Capability:
- AgentDefinition
- SkillDefinition
- SkillVersion
- ToolDefinition
- Connector
- Provider
- Capability
- Connection

Limits and budgets (ADR-0030; no plans, subscriptions or invoices):
- TenantLimit
- UsageRecord
- TenantBudget
- GlobalBudget
- BudgetReservation

Presence:
- PresenceSurface
- PresenceMeasurement
- PresenceScore
- PresenceScoreVersion
- AIVisibilityQuerySet
- AIVisibilitySample

Domains/deploy:
- Service
- Deployment
- Hostname
- DomainVerification
- CertificateState

Security/ops:
- SecretReference
- BrowserIdentity
- FileObject
- AuditEvent
- Incident
- FeatureFlag
- Release
- EvaluationRun
- ExecutionProfile

## 2026-08-10 additions

Tenant AI / model policy:
- TenantAIIdentity
- AIModelProfile
- TenantAIConfiguration
- TenantProviderPolicy
- ModelPolicyRevision

Digital properties:
- DigitalProperty
- PropertyEnvironment
- ServiceUnit
- HostnameAttachment
- PropertyDataBinding

Development factory:
- DevelopmentRun
- DevelopmentControllerProfile
- SandboxProfile
- GatePolicy
- TaskLease

## 2026-11-14 additions (ADR-0030)

Operator and client access:
- Invitation
- ClientRequest (queue item)
- ScheduledTask
- OperatorApproval
