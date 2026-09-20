# AWS Migration Guide

This document describes how to move the Cloud Cost Optimization Bot from the local Floci environment to real AWS infrastructure without changing the core control flow.

## Migration principle

Keep the application boundaries stable and replace only the local infrastructure adapters and demo data sources.

```text
Current local flow
Floci -> boto3 -> analyzer -> DynamoDB -> Telegram -> remediation

Target AWS flow
AWS EC2/CloudWatch/cost data -> boto3 -> analyzer -> DynamoDB -> Telegram -> EC2 remediation
```

## Current local components

| Current component | Purpose | Production direction |
|---|---|---|
| Floci EC2 API | Local EC2-compatible API | Amazon EC2 |
| Simulated CPU dataset | Reproducible idle state | CloudWatch CPU utilization |
| Simulated hourly rates | Demo savings model | AWS pricing / billing data |
| Floci-hosted DynamoDB API | Local persistence | Amazon DynamoDB |
| Docker Scheduler | Hourly processing | Containerized worker, scheduled job, or managed runtime |
| Streamlit | Operational dashboard | Keep Streamlit or replace with a managed UI |
| Telegram | Approval channel | Keep Telegram or replace with an enterprise notification system |

## 1. Replace Floci EC2 discovery

`app/scanner.py` already uses a boto3 EC2 client. The production implementation can keep the same service boundary but point the client at the normal AWS endpoint instead of the Floci endpoint.

Conceptually:

```python
session = boto3.Session(region_name=AWS_REGION)
ec2 = session.client("ec2", region_name=AWS_REGION)
```

The local endpoint override should be disabled in production.

## 2. Replace simulated CPU utilization

The current idle detector uses a deterministic local dataset so the demo is repeatable.

Production implementation:

```text
EC2 instance
     |
     v
CloudWatch CPU metric
     |
     v
idle detector
     |
     v
recommendation engine
```

A production implementation should define a sampling window rather than relying on one instantaneous value. For example, the design can evaluate a rolling average or a configurable low-utilization period before recommending a stop.

The exact threshold and observation window should be configurable rather than hard-coded.

## 3. Replace simulated cost rates

The current `cost_engine.py` intentionally uses demonstration values.

Production cost estimation should use authoritative AWS cost/pricing data appropriate to the deployed workload and account configuration.

A safer production model separates:

```text
actual observed spend
        +
resource runtime history
        +
current pricing assumptions
        =
estimated avoidable spend
```

Do not present the current local `730 × hourly_rate` calculation as actual AWS billing.

## 4. DynamoDB production deployment

The current data-access modules already define clear persistence boundaries. The production version can keep the same logical tables:

```text
cost-optimization-recommendations
cost-optimization-approvals
```

Production hardening should add:

- least-privilege IAM permissions
- encryption configuration appropriate to the environment
- backup and recovery policy
- retention policy
- conditional writes where needed for concurrency control
- indexes only where query patterns require them

## 5. IAM design

The production workload should use an IAM role rather than static credentials in environment variables.

The role should have only the permissions needed by each service.

Conceptually:

```text
Scheduler role
  -> read EC2 inventory
  -> read metrics
  -> write recommendations
  -> write approval records

Telegram bot / remediation role
  -> read approval
  -> describe target EC2
  -> stop only eligible EC2 resources
  -> update execution state

Dashboard role
  -> read-only access to operational data
```

The exact policy should be scoped to the application's real resource and action requirements.

## 6. Human approval in production

The current design intentionally requires explicit approval before remediation.

Recommended production flow:

```text
metric threshold met
       |
       v
recommendation
       |
       v
persist approval request
       |
       v
notification
       |
       v
human approval
       |
       v
re-check resource
       |
       v
execute stop
       |
       v
record result
```

The second validation step is important because a resource can change after the initial recommendation.

## 7. Production scheduling options

The local project uses APScheduler inside a long-running container.

For production, the same `run_monitoring_scan()` and `run_weekly_report()` boundaries can be triggered by a managed scheduler or another reliable scheduled-execution mechanism.

The important design requirement is that the business functions remain independent from the scheduler implementation.

## 8. Dashboard deployment

The Streamlit dashboard can remain containerized. The production deployment should place it behind the organization's normal access-control and network boundary.

The dashboard should remain read-oriented unless a deliberate administrative interface is added.

The existing remediation control plane should remain protected by Telegram authorization and server-side safety checks.

## 9. Secrets

Local development currently uses environment variables supplied by Docker Compose.

Production should move secrets such as the Telegram bot token to a managed secret mechanism rather than committing them to source control or plain-text Compose files.

Never commit:

```text
.env
real Telegram bot tokens
AWS access keys
private credentials
```

The repository should contain only placeholders such as `.env.example`.

## 10. Observability

The current scheduler already emits structured logs.

Production observability should track at least:

```text
scan success/failure
resources discovered
candidates detected
new recommendations
approval requests created
approval outcomes
remediation attempts
remediation successes/failures
estimated savings
```

The operational dashboard can expose the same metrics for a human operator.

## 11. Concurrency and idempotency

The current project prevents duplicate approval messages for an active recommendation.

Production should additionally consider concurrent scheduler instances and duplicate command delivery. DynamoDB conditional writes or an equivalent idempotency mechanism should be used so that two workers cannot both execute the same approval.

A remediation request should be treated as a state transition, not as a fire-and-forget command.

## 12. Production safety checklist

Before enabling remediation against real AWS resources:

- Replace simulated CPU metrics with production telemetry.
- Replace simulated cost estimates with authoritative cost data.
- Introduce IAM roles and least-privilege policies.
- Move secrets to managed secret storage.
- Add explicit resource allow/deny rules.
- Keep production resources protected by policy, not only by tags.
- Add concurrency-safe approval state transitions.
- Add an audit trail for every remediation attempt.
- Add a dry-run mode.
- Add rollback or restart handling appropriate to the resource lifecycle.
- Test against non-production AWS accounts before expanding scope.

## 13. Recommended production rollout

```text
Stage 1
Read-only discovery
        |
        v
Stage 2
Real metrics + real cost data
        |
        v
Stage 3
Recommendations only
        |
        v
Stage 4
Human-approved remediation
        |
        v
Stage 5
Expanded automation with explicit policy boundaries
```

The current project is designed to sit between Stage 3 and Stage 4 in the local environment: it generates recommendations, requires explicit approval, and supports approved remediation while keeping production and critical protections in place.
