# McDonalds Project - Burger Order Management with Observability

## Overview

This project is a web application for burger order management, built with:

- Flask backend
- SQLite database
- Web frontend (HTML/CSS/JavaScript) served by Flask
- JWT authentication
- Observability using OpenTelemetry + OTel Collector + Tempo + Grafana

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
- Grafana connects to Tempo for trace exploration

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
- Docker Desktop (for Grafana, Tempo, and OTel Collector)

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

- Grafana: `http://localhost:3000`
- Tempo API: `http://localhost:3200`
- OTel Collector OTLP gRPC: `localhost:4317`

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
4. Go to `Explore` and select the `tempo` datasource.
5. Search for recent traces from service `McDonalds-Backend-API`.
6. Confirm spans such as `POST /login`, `POST /pedidos`, and `GET /clientes`.

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

## Base Observability Status

Yes. Base observability is implemented and working:

- Flask instrumentation is active
- SQLite3 instrumentation is active
- OTLP export to the Collector is active
- Collector -> Tempo pipeline is active
- Traces are visible in Grafana

This provides a solid distributed tracing baseline for development and troubleshooting.

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
|   |-- prometheus.yml
|   `-- grafana/
|       |-- datasources.yaml
|       |-- dashboard-provisioning.yaml
|       `-- dashboards/
|-- requirements.txt
`-- README.md
```
