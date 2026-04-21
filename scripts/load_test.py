from __future__ import annotations

import argparse
import concurrent.futures
import json
import random
import threading
import time
import urllib.error
import urllib.request
from collections import Counter


DEFAULT_BASE_URL = "http://127.0.0.1:5000"
DEFAULT_USERNAME = "user1"
DEFAULT_PASSWORD = "password1"

RESULT_LOCK = threading.Lock()
RESULTS: Counter[str] = Counter()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate mixed traffic against the Flask API for Grafana/Prometheus demos."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--duration", type=int, default=90)
    parser.add_argument("--concurrency", type=int, default=12)
    parser.add_argument("--error-ratio", type=float, default=0.25)
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--customer-name", default="Load Test Customer")
    parser.add_argument("--customer-phone", default="900000001")
    parser.add_argument("--sleep-ms", type=int, default=25)
    return parser.parse_args()


def http_request(
    base_url: str,
    method: str,
    path: str,
    *,
    token: str | None = None,
    payload: dict | None = None,
    timeout: int = 10,
) -> tuple[int | None, float]:
    headers = {"Accept": "application/json"}
    body = None

    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")

    if token:
        headers["x-access-tokens"] = token

    request = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        headers=headers,
        method=method,
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
            return response.status, time.perf_counter() - start
    except urllib.error.HTTPError as exc:
        exc.read()
        return exc.code, time.perf_counter() - start
    except urllib.error.URLError:
        return None, time.perf_counter() - start


def login(base_url: str, username: str, password: str) -> str:
    status, _elapsed, body = request_json(
        base_url,
        "/login",
        {"username": username, "password": password},
    )
    if status != 200 or not isinstance(body, dict) or "token" not in body:
        raise RuntimeError(f"Login failed with status {status}: {body}")
    return body["token"]


def request_json(
    base_url: str,
    path: str,
    payload: dict,
    *,
    token: str | None = None,
) -> tuple[int | None, float, dict | str | None]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["x-access-tokens"] = token

    request = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
            try:
                return response.status, time.perf_counter() - start, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, time.perf_counter() - start, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            return exc.code, time.perf_counter() - start, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, time.perf_counter() - start, raw
    except urllib.error.URLError as exc:
        return None, time.perf_counter() - start, str(exc)


def worker(base_url: str, token: str, error_ratio: float, sleep_ms: int, stop_at: float) -> None:
    valid_order = {
        "nome_cliente": "Load Test Customer",
        "morada": "Test Street 1",
        "telefone": "900000001",
        "nome_hamburguer": "Big-Mac",
        "quantidade": 1,
        "tamanho": "normal",
    }

    while time.time() < stop_at:
        roll = random.random()
        if roll < error_ratio:
            status, elapsed = http_request(
                base_url,
                "POST",
                "/login",
                payload={"username": "user1", "password": "wrong-password"},
            )
            endpoint = "POST /login (invalid)"
        elif roll < 0.60:
            status, elapsed = http_request(base_url, "GET", "/clientes", token=token)
            endpoint = "GET /clientes"
        elif roll < 0.80:
            status, elapsed = http_request(base_url, "GET", "/hamburgueres", token=token)
            endpoint = "GET /hamburgueres"
        else:
            payload = dict(valid_order)
            payload["quantidade"] = random.randint(1, 3)
            payload["tamanho"] = random.choice(["infantil", "normal", "duplo"])
            status, elapsed = http_request(
                base_url,
                "POST",
                "/pedidos",
                token=token,
                payload=payload,
            )
            endpoint = "POST /pedidos"

        with RESULT_LOCK:
            RESULTS["total"] += 1
            RESULTS[f"status_{status if status is not None else 'timeout'}"] += 1
            RESULTS[f"endpoint_{endpoint}"] += 1
            RESULTS["latency_sum_ms"] += elapsed * 1000

        time.sleep(sleep_ms / 1000)


def ensure_customer(base_url: str, token: str) -> None:
    request_json(
        base_url,
        "/clientes",
        {
            "nome": "Load Test Customer",
            "morada": "Test Street 1",
            "telefone": "900000001",
        },
        token=token,
    )


def main() -> int:
    args = parse_args()
    stop_at = time.time() + args.duration

    print(f"Base URL: {args.base_url}")
    print(f"Duration: {args.duration}s | Concurrency: {args.concurrency} | Error ratio: {args.error_ratio:.0%}")

    token = login(args.base_url, args.username, args.password)
    ensure_customer(args.base_url, token)

    print("Load test started. Open Grafana and Prometheus to watch metrics and alerts live.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(worker, args.base_url, token, args.error_ratio, args.sleep_ms, stop_at)
            for _ in range(args.concurrency)
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    total = RESULTS["total"] or 1
    avg_latency = RESULTS["latency_sum_ms"] / total

    print("\nSummary")
    print(f"Total requests: {RESULTS['total']}")
    print(f"Average latency: {avg_latency:.2f} ms")
    print("Status counts:")
    for key, value in sorted(RESULTS.items()):
        if key.startswith("status_"):
            print(f"  {key.replace('status_', '')}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())