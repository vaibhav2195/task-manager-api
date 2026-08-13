import time
from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP request count",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

ACTIVE_REQUESTS = Gauge(
    "http_requests_active",
    "Number of active HTTP requests",
)

TASK_COUNT_GAUGE = Gauge(
    "task_manager_total_tasks",
    "Total number of tasks stored in the system",
)


async def prometheus_middleware(request: Request, call_next):
    """Middleware for recording HTTP request metrics."""
    ACTIVE_REQUESTS.inc()
    start_time = time.time()

    # Avoid counting /metrics itself in latency histograms if desired, but record path
    path = request.url.path
    method = request.method

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception as exc:
        status_code = "500"
        raise exc from None
    finally:
        latency = time.time() - start_time
        ACTIVE_REQUESTS.dec()
        REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(latency)

    return response


def get_metrics_response() -> Response:
    """Generate Prometheus formatted metrics payload."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
