
import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import urlsplit

import requests

LOG_DIR = Path("reports/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "automation.jsonl"

logger = logging.getLogger("saucedemo")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def log_event(event, level="INFO", **details):
    record = {
        "timestamp": time.time(),
        "level": level,
        "event": event,
        "application": "saucedemo-automation",
        "build_number": os.getenv("BUILD_NUMBER", "local"),
        **details,
    }

    line = json.dumps(record, default=str)

    # Always keep a local log, even if Grafana is unavailable.
    logger.info(line)

    base_url = os.getenv("GRAFANA_LOKI_URL", "").rstrip("/")
    username = os.getenv("GRAFANA_LOKI_USERNAME", "")
    token = os.getenv("GRAFANA_LOKI_TOKEN", "")

    # Local logging works without Grafana credentials.
    if not (base_url and username and token):
        return

    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.netloc:
        print("Grafana logging skipped: invalid HTTPS URL.")
        return

    if parsed.path.endswith("/loki/api/v1/push"):
        push_url = base_url
    else:
        push_url = base_url + "/loki/api/v1/push"

    timestamp_ns = str(time.time_ns())

    payload = {
        "streams": [
            {
                "stream": {
                    "job": "saucedemo-automation",
                    "level": level,
                },
                "values": [
                    [timestamp_ns, line]
                ],
            }
        ]
    }

    try:
        response = requests.post(
            push_url,
            json=payload,
            auth=(username, token),
            timeout=5,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        # Don't fail the automation test because log delivery failed.
        print(f"Grafana log delivery failed: {exc}")
