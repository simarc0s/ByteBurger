# McDonalds Project - Burger Order Management with Observability

## Overview

This project is a web application for burger order management, built with:

- Flask backend
- SQLite database
- Web frontend (HTML/CSS/JavaScript) served by Flask
- JWT authentication
- Observability using OpenTelemetry + OTel Collector + Tempo + Prometheus + Grafana + Loki + Mimir

Note: the old Kivy frontend was removed due to Python 3.14 compatibility issues.

## Architecture

### Application

- `app/FlaskServer.py`: REST API, authentication, order logic, and web routes
- `templates/login.html`: login page
- `templates/orders.html`: order creation page
- `static/images/`: burger images
- `data/database.db`: SQLite database
- `app/tablesdb.py`: schema setup/migration and initial seed script

### Observability

- Flask exports OTLP gRPC traces to `localhost:4317`
- OTel Collector receives traces on `4317/4318` and forwards them to Tempo
- Tempo stores traces and exposes its HTTP API on `3200`
- Prometheus scrapes metrics from Flask `/metrics` endpoint on `9090`
- Mimir provides long-term storage backend for Prometheus metrics on `9009`
- Loki aggregates and stores logs from all containers (`3100`)
- Promtail is a log collector agent that sends logs to Loki
- Grafana connects to Tempo (traces), Prometheus (metrics), Loki (logs), and Mimir (historical metrics)

## Features

- JWT login (`/login`)
- Create customers (`POST /clientes`)
- Create orders (`POST /pedidos`)
- Find customer by phone (`GET /clientes/<telefone>`)
- Find customers by name (`GET /clientes/nome/<nome>`)
- List all customers (`GET /clientes`)
- List burgers (`GET /hamburgueres`)
- Health check (`GET /health`)
- Web UI endpoints: `GET /ui/login`, `GET /ui/orders`

## Requirements

- Python 3.14+
- Docker Desktop (for Grafana, Tempo, OTel Collector, Prometheus, Mimir, Loki, and Promtail)

Install Python dependencies:

```sh
python -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
```

## Environment Configuration (Optional)

Supported backend environment variables:

- `SECRET_KEY`: JWT signing key
- `OTEL_SERVICE_NAME`: service name shown in traces (default: `McDonalds-Backend-API`)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP gRPC endpoint (default: `localhost:4317`)

PowerShell example:

```powershell
$env:SECRET_KEY="change-this-key-in-production"
$env:OTEL_SERVICE_NAME="McDonalds-Backend-API"
$env:OTEL_EXPORTER_OTLP_ENDPOINT="localhost:4317"
```

## How to Run

### 1. Initialize the database (run once, or when you need a schema reset)

```sh
.venv\\Scripts\\python.exe app/tablesdb.py
```

Default seed credentials:

- `username`: `user1`
- `password`: `password1`

### 2. Start the observability stack

```sh
docker compose up -d
```

Services:

- Grafana: `http://localhost:3000` (unified observability dashboard)
- Tempo: `http://localhost:3200` (distributed tracing API)
- OTel Collector OTLP gRPC: `localhost:4317` (trace ingestion)
- Prometheus: `http://localhost:9090` (metrics scraper)
- Mimir: `http://localhost:9009` (long-term metrics storage backend)
- Loki: `http://localhost:3100` (log aggregation backend)
- Promtail: log collector agent (no UI)

### 3. Start the Flask backend

```sh
.venv\\Scripts\\python.exe app/FlaskServer.py
```

Application URLs:

- Login UI: `http://127.0.0.1:5000/ui/login`
- Orders UI: `http://127.0.0.1:5000/ui/orders`
- Health check: `http://127.0.0.1:5000/health`

## Quick End-to-End Test

1. Open `http://127.0.0.1:5000/ui/login` and log in with `user1/password1`.
2. Create an order in the UI.
3. Open Grafana at `http://localhost:3000`.
4. Go to `Explore` panel to see multiple data sources:
   - **Tempo**: Search for recent traces from service `McDonalds-Backend-API` (spans like `POST /login`, `POST /pedidos`, `GET /clientes`)
   - **Prometheus**: View real-time metrics (CPU, memory, request rates)
   - **Mimir**: Query historical metrics from Prometheus
   - **Loki**: Stream and search container logs from the observability stack

## Clear Database Data

To delete all orders and customers while keeping the schema and users:

```python
import sqlite3

conn = sqlite3.connect("data/database.db")
cur = conn.cursor()
cur.execute("DELETE FROM pedidos")
cur.execute("DELETE FROM clientes")
cur.execute("DELETE FROM sqlite_sequence")
conn.commit()
conn.close()
```

## Observability Stack Status

**Complete observability suite implemented and working:**

- ✅ Distributed tracing: Flask instrumentation + OTel Collector → Tempo (OTLP gRPC/HTTP)
- ✅ Real-time metrics: Prometheus scraping Flask `/metrics` endpoint
- ✅ Long-term metrics storage: Mimir backend for Prometheus data retention (8760 hours = 1 year)
- ✅ Log aggregation: Promtail collecting container logs → Loki central storage
- ✅ SQLite3 instrumentation: Database queries traced and exported
- ✅ Unified observability UI: Grafana with 4 datasources (Tempo, Prometheus, Mimir, Loki)

This provides enterprise-grade observability for development, staging, and production environments.

## Project Structure

```text
.
|-- app/
|   |-- FlaskServer.py
|   `-- tablesdb.py
|-- data/
|   `-- database.db
|-- templates/
|   |-- login.html
|   `-- orders.html
|-- static/
|   `-- images/
|-- docker-compose.yml
|-- observability/
|   |-- otel-collector-config.yaml
|   |-- tempo-config.yaml
|   |-- loki-config.yaml
|   |-- mimir-config.yaml
|   |-- promtail-config.yaml
|   |-- prometheus.yml
|   `-- grafana/
|       |-- datasources.yaml
|       |-- dashboard-provisioning.yaml
|       `-- dashboards/
|-- requirements.txt
`-- README.md
```
