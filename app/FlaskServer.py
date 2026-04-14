import datetime
import logging
import os
import sqlite3
import time
from pathlib import Path
from functools import wraps

import jwt
from flask import Flask, jsonify, make_response, redirect, render_template, request, url_for
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

# --- 1. OPENTELEMETRY IMPORTS ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# New: OTLP Exporter to send data to Docker
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry.sdk.resources import Resource
# -----------------------------------


class TraceContextFilter(logging.Filter):
    """Inject trace and span IDs into log records for correlation."""

    def filter(self, record):
        span = trace.get_current_span()
        span_context = span.get_span_context()

        if span_context and span_context.is_valid:
            record.trace_id = format(span_context.trace_id, "032x")
            record.span_id = format(span_context.span_id, "016x")
        else:
            record.trace_id = "-"
            record.span_id = "-"

        return True


REQUEST_COUNT = Counter(
    "http_server_requests_total",
    "Total number of HTTP requests processed by Flask.",
    ["method", "route", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_server_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "route"],
)

# Initialize the Flask application and configure the secret key
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / "data" / "database.db"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "change-me-in-production-use-a-strong-secret-key-with-32-plus-bytes",
)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s [trace_id=%(trace_id)s span_id=%(span_id)s] %(message)s"
    )
)
handler.addFilter(TraceContextFilter())

app.logger.handlers.clear()
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.propagate = False

# --- 2. OPENTELEMETRY SETUP ---
# Give your service a clear name so it's easy to find in Grafana
resource = Resource.create(
    {"service.name": os.getenv("OTEL_SERVICE_NAME", "McDonalds-Backend-API")}
)
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Point the exporter to the OTel Collector running in Docker on port 4317
# NOTE: gRPC endpoint must be 'host:port' without the http:// scheme
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
    insecure=True,
)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)

# Turn on automatic instrumentation for Flask and SQLite3
FlaskInstrumentor().instrument_app(app)
SQLite3Instrumentor().instrument()
# ----------------------------------------


@app.before_request
def start_request_timer():
    request._start_time = time.perf_counter()


@app.after_request
def record_request_metrics(response):
    route = request.url_rule.rule if request.url_rule else request.path
    method = request.method
    status_code = str(response.status_code)

    REQUEST_COUNT.labels(method=method, route=route, status_code=status_code).inc()

    start_time = getattr(request, "_start_time", None)
    if start_time is not None:
        REQUEST_LATENCY.labels(method=method, route=route).observe(
            time.perf_counter() - start_time
        )

    return response

if (
    app.config["SECRET_KEY"]
    == "change-me-in-production-use-a-strong-secret-key-with-32-plus-bytes"
):
    app.logger.warning(
        "Using default SECRET_KEY. Set SECRET_KEY environment variable before production use."
    )


# Returns a new SQLite database connection
def getdb():
    conn = sqlite3.connect(str(DATABASE))
    return conn


def require_json_fields(payload, required_fields):
    """Returns an error response tuple if payload is invalid; otherwise None."""
    if not payload:
        return jsonify({"message": "Request body must be valid JSON"}), 400

    missing = [field for field in required_fields if field not in payload]
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    return None

# Decorator that enforces JWT authentication on protected routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("x-access-tokens")
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = data["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403
        return f(current_user, *args, **kwargs)

    return decorated


# Route to log in and obtain a JWT authentication token
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    validation_error = require_json_fields(auth, ["username", "password"])
    if validation_error:
        return validation_error

    username = auth["username"]
    password = auth["password"]

    conn = getdb()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return make_response(
            "Could not verify credentials",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required!"'},
        )

    token = jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(minutes=30),
        },
        app.config["SECRET_KEY"],
    )
    return jsonify({"token": token})


# Route to add a new customer, protected by token
@app.route("/clientes", methods=["POST"])
@token_required
def addcliente(_current_user):
    data = request.get_json()
    validation_error = require_json_fields(data, ["nome", "morada", "telefone"])
    if validation_error:
        return validation_error

    conn = getdb()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
        (data["nome"], data["morada"], data["telefone"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201


# Route to add a new order, protected by token
@app.route("/pedidos", methods=["POST"])
@token_required
def add_pedido(_current_user):
    data = request.get_json()
    validation_error = require_json_fields(
        data,
        [
            "nome_cliente",
            "morada",
            "telefone",
            "nome_hamburguer",
            "quantidade",
            "tamanho",
        ],
    )
    if validation_error:
        return validation_error

    app.logger.info(f"Data received: {data}")
    conn = getdb()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_cliente FROM clientes WHERE telefone = ?", (data["telefone"],)
    )
    cliente = cursor.fetchone()
    if cliente is None:
        cursor.execute(
            "INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
            (data["nome_cliente"], data["morada"], data["telefone"]),
        )
        conn.commit()
        cliente_id = cursor.lastrowid
    else:
        cliente_id = cliente[0]

    valor_total = calcular_valor_total(
        data["nome_hamburguer"], data["quantidade"], data["tamanho"]
    )

    cursor.execute(
        "INSERT INTO pedidos (id_cliente, nome_hamburguer, quantidade, tamanho, valor_total) VALUES (?, ?, ?, ?, ?)",
        (
            cliente_id,
            data["nome_hamburguer"],
            data["quantidade"],
            data["tamanho"],
            valor_total,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201


# Route to find a customer by phone number, protected by token
@app.route("/clientes/<telefone>", methods=["GET"])
@token_required
def encontrar_cliente_por_telefone(_current_user, telefone):
    conn = getdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE telefone = ?", (telefone,))
    cliente = cursor.fetchone()
    conn.close()

    if cliente:
        return jsonify(
            {
                "id_cliente": cliente[0],
                "nome": cliente[1],
                "morada": cliente[2],
                "telefone": cliente[3],
            }
        )
    else:
        return jsonify({"message": "Customer not found"}), 404


# Route to find customers by name, protected by token
@app.route("/clientes/nome/<nome>", methods=["GET"])
@token_required
def encontrar_cliente_por_nome(_current_user, nome):
    conn = getdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE nome LIKE ?", ("%" + nome + "%",))
    clientes = cursor.fetchall()
    conn.close()

    if clientes:
        result = []
        for cliente in clientes:
            result.append(
                {
                    "id_cliente": cliente[0],
                    "nome": cliente[1],
                    "morada": cliente[2],
                    "telefone": cliente[3],
                }
            )
        return jsonify(result)
    else:
        return jsonify({"message": "No customers found with that name"}), 404


# Route to list all customers, protected by token
@app.route("/clientes", methods=["GET"])
@token_required
def listar_todos_clientes(_current_user):
    conn = getdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()

    if clientes:
        result = []
        for cliente in clientes:
            result.append(
                {
                    "id_cliente": cliente[0],
                    "nome": cliente[1],
                    "morada": cliente[2],
                    "telefone": cliente[3],
                }
            )
        return jsonify(result)
    else:
        return jsonify({"message": "No customers found"}), 404


# Route to list all burgers, protected by token
@app.route("/hamburgueres", methods=["GET"])
@token_required
def listar_todos_hamburgueres(_current_user):
    conn = getdb()
    cursor = conn.cursor()
    cursor.execute("SELECT nome_hamburguer, imagem_url, ingredientes FROM hamburgueres")
    hamburgueres = cursor.fetchall()
    conn.close()

    if hamburgueres:
        result = [
            {
                "nome": hamburguer[0],
                "imagem_url": hamburguer[1],
                "ingredientes": hamburguer[2],
            }
            for hamburguer in hamburgueres
        ]
        return jsonify(result)
    else:
        return jsonify({"message": "No burgers found"}), 404


# Calculates the total price of an order based on size multiplier
def calcular_valor_total(nome_hamburguer, quantidade, tamanho):
    preco_base = 5.0
    multiplicador_tamanho = {"infantil": 0.75, "normal": 1.0, "duplo": 1.5}
    return preco_base * int(quantidade) * multiplicador_tamanho.get(tamanho, 1.0)


# --- WEB UI ROUTES ---


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/")
def index():
    # Redirect root to the login page
    return redirect(url_for("ui_login"))

@app.route("/ui/login")
def ui_login():
    return render_template("login.html")

@app.route("/ui/orders")
def ui_orders():
    return render_template("orders.html")
# ---------------------


# Start the Flask development server
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")