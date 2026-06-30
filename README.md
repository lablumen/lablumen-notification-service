# lablumen-notification-service

A lightweight event consumer that listens to an SQS queue and sends transactional emails via Amazon SES. It runs as a persistent pod in EKS alongside the other services but has no direct user-facing API traffic.

---

## Responsibilities

- Long-polls the `lablumen-notifications` SQS queue every 20 seconds.
- Parses each message as a typed notification event and sends the corresponding email via SES.
- Deletes the message from SQS only after a successful send. Failed sends remain on the queue for automatic retry.
- Exposes a `/healthz` endpoint used by the Kubernetes liveness probe and ALB health check.

---

## Event Types

| Event | Email Subject |
|---|---|
| `appointment.booked` | Your LabLumen appointment is confirmed |
| `appointment.cancelled` | Your LabLumen appointment was cancelled |
| `report.ready` | Your LabLumen lab report is ready |

Events are published by the appointment service and (when implemented) the report service. This service only consumes — it has no knowledge of how events are produced.

---

## Tech Stack

| Component | Detail |
|---|---|
| Runtime | Python 3.12 |
| Framework | FastAPI (health endpoint only) |
| Messaging | AWS SQS (boto3, 20-second long-poll) |
| Email | AWS SES (boto3) |
| Validation | Pydantic v2 |

---

## Source Layout

```
app/
  main.py      FastAPI entry point; starts the SQS consumer as an async background task (lifespan)
  consumer.py  consume_forever() loop — polls SQS, dispatches events, handles retries
  emailer.py   Sends formatted emails via SES (source: no-reply@rnld101.xyz)
  events.py    Pydantic models for incoming SQS message payloads
  config.py    Settings from environment variables
  routers/
    health.py  /healthz liveness probe
```

---

## Configuration

All values are injected by External Secrets Operator from AWS at pod startup.

| Variable | Source | Description |
|---|---|---|
| `NOTIFICATIONS_QUEUE_URL` | SSM | SQS queue URL to poll |
| `SES_SENDER` | SSM | Sender address (`no-reply@rnld101.xyz`) |
| `AWS_REGION` | SSM | AWS region |

---

## CI/CD

| Trigger | What Happens |
|---|---|
| Pull request | Lint (`ruff`), unit tests (`pytest`), SAST (SonarCloud), SCA (Snyk), container scan (Trivy) |
| Merge to `main` | Build image → Trivy gate → push to ECR → update `values-dev.yaml` → ArgoCD deploys to dev |
| GitHub Release | Retag ECR image SHA → semver → update `values-prod.yaml` → ArgoCD deploys to production |

CI/CD logic is centralized in `lablumen-shared`.
