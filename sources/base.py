import requests
import logging
from typing import Callable, List
from models import Job

log = logging.getLogger("qa-radar")

HEADERS = {"User-Agent": "qa-radar/1.0 (github.com)"}


def http_get_json(url: str, params=None, headers=None, timeout: int = 20):
    hdrs = {**HEADERS, **(headers or {})}
    r = requests.get(url, params=params, headers=hdrs, timeout=timeout)
    r.raise_for_status()
    return r.json()


def safe_fetch(fn: Callable[[], List[Job]], label: str) -> List[Job]:
    try:
        return fn()
    except Exception as e:
        log.warning("source %s failed: %s", label, e)
        return []
