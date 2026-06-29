from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://remoteok.com/api"


def parse_remoteok(data: list) -> List[Job]:
    jobs = []
    for item in data:
        if not isinstance(item, dict) or "position" not in item:
            continue
        jobs.append(Job(
            source="remoteok",
            company=item.get("company", ""),
            title=item.get("position", ""),
            location=item.get("location", "Remote"),
            url=item.get("url", ""),
            posted_at=item.get("date"),
        ))
    return jobs


def fetch() -> List[Job]:
    return safe_fetch(
        lambda: parse_remoteok(http_get_json(API)),
        "remoteok"
    )
