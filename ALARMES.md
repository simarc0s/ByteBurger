# Simple Alerts - Usage Guide

## Configured Alerts

### 1. HighErrorRate (WARNING)
- Condition: Error rate > 5% for 2 minutes.
- What to do: Check logs in Grafana (Loki).
- Common causes: Invalid credentials, database issues, bad client payloads.

### 2. HighLatency (WARNING)
- Condition: P95 latency > 500ms for 2 minutes.
- What to do: Check request duration metrics and database performance.
- Common causes: Slow queries, high concurrency, resource saturation.

### 3. ServiceDown (CRITICAL)
- Condition: Flask /health endpoint is down for 1 minute.
- What to do: Restart services and inspect container logs.
- Common causes: App crash, port conflicts, startup failures.

### 4. HighMemoryUsage (WARNING)
- Condition: Process memory > 500MB for 2 minutes.
- What to do: Review workload and restart app if needed.
- Common causes: Memory leak, heavy load, too many open resources.

## Email Notification Setup

### Step 1: Configure SMTP settings

Run in PowerShell:

```powershell
$env:EMAIL_ALERT_TO = "simao.bmarcos@gmail.com"
$env:GF_SMTP_HOST = "smtp.gmail.com:587"
$env:GF_SMTP_USER = "simao.bmarcos@gmail.com"
$env:GF_SMTP_PASSWORD = "YOUR_GMAIL_APP_PASSWORD"
$env:GF_SMTP_FROM_ADDRESS = "simao.bmarcos@gmail.com"
docker compose up -d
```

### Step 2: Validate notifications

1. Open Grafana at http://localhost:3000.
2. Open Alertmanager at http://localhost:9093.
3. Trigger an alert and check your inbox/spam folder.

## Where To Check Alerts

### Grafana
- http://localhost:3000/alerting/list: Notification history and alert state.

### Prometheus
- http://localhost:9090/alerts: Rule evaluation and firing state.

### Alertmanager
- http://localhost:9093: Active alerts and receiver routing.

## Edit Alert Thresholds

1. Edit observability/prometheus-rules.yml.
2. Update thresholds (example: 0.05 to 0.10 for 10% error rate).
3. Restart Prometheus:

```powershell
docker compose restart prometheus
```

## Troubleshooting

If alerts do not appear:
- Restart services:

```powershell
docker compose restart prometheus alertmanager grafana
```

- Check logs:

```powershell
docker compose logs prometheus
docker compose logs alertmanager
```

If email does not arrive:
- Verify SMTP user/password.
- Verify Gmail App Password is used (not your normal password).
- Check Inbox, Spam, and Promotions folders.
