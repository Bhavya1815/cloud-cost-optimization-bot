# Architecture

## Overview

The Cloud Cost Optimization Bot is split into four runtime services plus DynamoDB-backed persistence inside the local Floci environment.

```text
                           Docker Compose
+-------------------------------------------------------------------+
|                                                                   |
|  +-------------------+                                            |
|  |       Floci       |                                            |
|  | AWS-compatible    |                                            |
|  | local environment |                                            |
|  +---------+---------+                                            |
|            |                                                      |
|     HTTP AWS-compatible API                                      |
|            |                                                      |
|    +-------+----------------------+                               |
|    |                              |                               |
| +--v-----------+          +-------v----------+                    |
| |  Scheduler   |          |    Dashboard     |                    |
| | hourly scan |          |    Streamlit     |                    |
| +--+-----------+          +------------------+                    |
|    |                                                              |
|    | recommendations                                              |
|    v                                                              |
| +-------------------+                                             |
| |     DynamoDB      |<-----------------------------+              |
| | recommendations   |                              |              |
| | approvals         |                              |              |
| +---------+---------+                              |              |
|           |                                        |              |
|           v                                        |              |
| +-------------------+                              |              |
| | Telegram Notifier |                              |              |
| +---------+---------+                              |              |
|           |                                        |              |
|           v                                        |              |
|       Telegram API                                  |              |
|                                                    |              |
| +-------------------+                              |              |
| |   Telegram Bot    |------------------------------+              |
| | /approve /reject  |                                             |
| | /status /start   |                                             |
| +---------+---------+                                             |
|           |                                                       |
|           v                                                       |
| +-------------------+                                             |
| |    Remediation    |                                             |
| |    safety gates   |                                             |
| +---------+---------+                                             |
|           |                                                       |
|           v                                                       |
|       EC2 stop API                                                 |
|                                                                   |
+-------------------------------------------------------------------+
```

## Components

### `aws_client.py`

Creates boto3 sessions and EC2 clients using endpoint and credential configuration supplied through environment variables. This keeps local Docker credentials separate from workstation profiles.

### `scanner.py`

Discovers EC2 instances and normalizes the small subset of metadata required by the optimizer:

- instance ID
- instance type
- state
- Name tag
- environment
- cost-optimization tag
- critical tag

### `idle_detector.py`

Adds CPU utilization and idle state to discovered resources. In the current local implementation these CPU values are simulated so the workflow can be reproduced without real CloudWatch data.

### `analyzer.py`

Applies optimization rules. A recommendation is produced only when the resource is:

- running
- idle
- explicitly marked for cost optimization
- not critical
- not production

### `cost_engine.py`

Calculates demonstration monthly cost and savings:

```text
monthly estimate = simulated hourly rate × 730 hours
```

### `dynamodb_store.py`

Stores recommendation state and prevents duplicate notifications. A resource that remains an active candidate stays `ACTIVE`; a recommendation that disappears is marked `RESOLVED`; a previously resolved resource that becomes a candidate again can create a new recommendation.

### `approval.py`

Creates an approval object and controls the legal state transitions for approval and rejection.

### `approval_store.py`

Persists approval requests to DynamoDB.

### `remediation.py`

Contains the final safety gate before an EC2 stop operation.

### `remediation_service.py`

Loads an approved request, re-scans the target resource, runs safety checks again, executes the stop request, and records `EXECUTED` or `FAILED`.

### `scheduler.py`

Runs the hourly scan and weekly report jobs using APScheduler.

### `telegram_bot.py`

Implements the human-in-the-loop control plane:

```text
/start
/approve <approval_id>
/reject <approval_id>
/status <approval_id>
```

Authorization is restricted to the configured Telegram chat ID.

### `dashboard.py`

Provides operational visibility into resource state, CPU activity, optimization candidates, estimated savings, approval state, and resource inventory.

## State machines

### Recommendation lifecycle

```text
                candidate found
                      |
                      v
                    NEW
                      |
                      v
                    ACTIVE
                   /      \
        candidate gone   candidate remains
              |                |
              v                +----> ACTIVE
           RESOLVED
              |
              | candidate returns
              v
             NEW
```

### Approval lifecycle

```text
PENDING
  |  \
  |   \
  v    v
APPROVED  REJECTED
  |
  v
EXECUTED
```

Failure during remediation results in:

```text
APPROVED -> FAILED
```

## Safety boundaries

There are two independent protection layers.

### Recommendation layer

Prevents creation of optimization recommendations for production and critical resources.

### Remediation layer

Re-validates the resource immediately before a stop request. This protects against state or tag changes that occurred after the recommendation was generated.

## Failure handling

The scheduler logs exceptions and re-raises them so container-level failures remain visible. Docker restart policies provide process-level recovery.

The remediation service marks failed executions in DynamoDB so an operational failure is not silently treated as success.

## Persistence

The Floci container mounts a named volume at:

```text
/app/data
```

and runs with hybrid storage configuration. The project was verified by restarting the Floci container and confirming that the EC2 resource state remained available afterward.

## Local versus production boundary

The architecture intentionally separates interfaces from implementation details.

### Local implementation

```text
Floci
Simulated CPU
Simulated cost rates
Local DynamoDB emulator
```

### Production target

```text
AWS EC2
CloudWatch metrics
AWS cost/billing data
Amazon DynamoDB
Telegram or another approved notification channel
```

The migration should preserve the recommendation, approval, safety, and remediation boundaries while replacing the emulator-specific data sources.
