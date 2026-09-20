# Cloud Cost Optimization Bot

A Dockerized cloud-cost optimization platform that discovers running compute resources, identifies idle non-production resources, estimates potential savings, creates approval requests, and executes approved remediation through a Telegram control bot.

## Project status

The local implementation is fully functional and validated with automated tests.

- Floci-based AWS-compatible local environment
- Persistent Floci state using `/app/data` with hybrid storage
- EC2 resource discovery with boto3
- Simulated CPU utilization for local demonstration
- Simulated EC2 hourly rates for local demonstration
- DynamoDB recommendation and approval storage
- Hourly monitoring scheduler
- Weekly Telegram report generation
- Telegram approval/rejection/status commands
- Safety gates for production, critical, non-optimized, non-idle, and non-running resources
- Explicit-approval remediation workflow
- Streamlit dashboard
- Docker Compose deployment
- Automated test suite: 19 tests passing

> **Important:** This local project uses Floci as an AWS emulator. CPU metrics are simulated and cost figures are simulated estimates. They are not real AWS CloudWatch measurements or AWS billing charges.

## Architecture

```text
                         +----------------------+
                         |        Floci         |
                         | AWS-compatible local |
                         |     environment      |
                         +----------+-----------+
                                    |
                  +-----------------+------------------+
                  |                 |                  |
           +------v------+   +------v------+   +-------v--------+
           |  Scheduler  |   |  Dashboard  |   |  Telegram Bot  |
           | Hourly scan |   |  Streamlit  |   | Approve/Reject |
           +------+------+
                  |
        +---------+----------+
        |                    |
 +------v------+      +------v-------+
 |  DynamoDB   |      | Cost / Idle  |
 | Recommendations     | Analysis     |
 | Approvals   |      +--------------+
 +------+------+
        |
 +------v-------+
 | Remediation  |
 | Safety Gates |
 +--------------+
```

## Core workflow

1. Discover EC2 instances through boto3.
2. Enrich resources with tags such as `Environment`, `CostOptimization`, and `Critical`.
3. Determine idle status using the local simulated CPU dataset.
4. Generate optimization candidates only for eligible non-production resources.
5. Estimate monthly cost and savings using local demonstration rates.
6. Persist recommendations in DynamoDB.
7. Prevent duplicate alerts for already-active recommendations.
8. Create an approval request for a new recommendation.
9. Send the recommendation to Telegram.
10. Receive `/approve`, `/reject`, or `/status` commands through the Telegram control bot.
11. Re-check safety gates before remediation.
12. Execute an approved EC2 stop request.
13. Update approval execution state in DynamoDB.
14. Reflect the resulting resource state in the dashboard.

## Safety model

The remediation layer refuses to stop a resource when any of the following is true:

- resource is not running
- environment is `prod`
- resource is marked `Critical=true`
- resource is not marked `CostOptimization=true`
- resource is not currently idle

No resource is stopped from the monitoring scan alone. Remediation requires an explicit approval.

## Services

| Service | Purpose | Port / Interface |
|---|---|---|
| `floci` | Local AWS-compatible environment | `4566` |
| `dashboard` | Streamlit monitoring dashboard | `8501` |
| `scheduler` | Hourly monitoring and weekly reports | internal |
| `telegram-bot` | Approval and control commands | Telegram polling |

## Project structure

```text
cloud-cost-optimizer/
├── app/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── approval.py
│   ├── approval_store.py
│   ├── aws_client.py
│   ├── config.py
│   ├── cost_engine.py
│   ├── dashboard.py
│   ├── dynamodb_store.py
│   ├── idle_detector.py
│   ├── logging_config.py
│   ├── main.py
│   ├── remediation.py
│   ├── remediation_service.py
│   ├── report_generator.py
│   ├── scanner.py
│   ├── scheduler.py
│   ├── telegram_bot.py
│   ├── telegram_formatter.py
│   └── telegram_notifier.py
├── tests/
│   ├── test_analyzer.py
│   ├── test_approval.py
│   ├── test_cost_engine.py
│   └── test_remediation.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── ARCHITECTURE.md
├── AWS-MIGRATION.md
└── README.md
```

## Local setup

### Prerequisites

- Windows with Docker Desktop and WSL2, or an equivalent Docker environment
- Python 3.13+
- AWS CLI
- A Telegram bot and chat ID

### Python environment

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

### Environment variables

Use `.env.example` as the template. Keep the real Telegram bot token out of Git.

PowerShell example:

```powershell
$env:TELEGRAM_BOT_TOKEN="YOUR_CURRENT_TOKEN"
$env:TELEGRAM_CHAT_ID="2138357235"
```

### Start the stack

```powershell
docker compose config
docker compose up -d
```

Check service health:

```powershell
docker compose ps
```

The dashboard is available at:

```text
http://localhost:8501
```

### Verify the scheduler

```powershell
docker logs cloud-cost-optimizer-scheduler --tail 50
```

### Verify the Telegram control bot

```powershell
docker logs cloud-cost-optimizer-telegram-bot --tail 50
```

Then send `/start` to the Telegram bot.

## Running tests

From the project root:

```powershell
python -m pytest -q
```

Current validated result:

```text
19 passed
```

## Demo resource model

The local environment uses tags to make safety behavior explicit.

Example development candidate:

```text
Name=dev-idle-03
Environment=dev
CostOptimization=true
Critical=false
```

Example protected production resource:

```text
Name=production-01
Environment=prod
CostOptimization=true
Critical=false
```

A development resource with `Critical=true` is also protected.

## Telegram commands

The Telegram control bot supports:

```text
/start
/approve <approval_id>
/reject <approval_id>
/status <approval_id>
```

Only the configured Telegram chat ID is authorized to execute these commands.

## Persistence

Floci is configured to use hybrid storage with `/app/data` mounted to a named Docker volume. The Docker environment has been tested by restarting the Floci container and confirming that the EC2 resource state remained available.

## Observability

The scheduler uses structured application logging with timestamps and log levels. Docker service health is exposed through Compose health checks for Floci and the Streamlit dashboard.

## Cost model disclaimer

The local project deliberately uses simulated values for demonstration:

- CPU utilization is supplied by the local idle-detector dataset.
- EC2 hourly rates are stored in `app/config.py` as demonstration values.
- Monthly cost is calculated as hourly rate multiplied by `730` hours.

These values must not be presented as actual AWS charges.

## AWS migration direction

The local design can be migrated by replacing the emulator-specific pieces with AWS services while keeping most of the application boundaries intact. See [AWS-MIGRATION.md](AWS-MIGRATION.md).

## Portfolio description

> Built a cloud cost optimization bot that automatically detects idle resources, calculates simulated savings recommendations, sends approval requests through Telegram, and executes approved remediation with safety controls.

## Engineering highlights

- boto3-based infrastructure discovery
- event-safe approval workflow
- persistent recommendation state
- duplicate-alert prevention
- containerized scheduler and control bot
- explicit remediation safety gates
- automated tests
- Streamlit operational dashboard
