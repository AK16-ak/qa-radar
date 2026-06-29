from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://www.arbeitnow.com/api/job-board-api"


def parse_arbeitnow(data: dict) -> List[Job]:
    jobs = []
    for item in data.get("data", []):
        location = item.get("location", "")
        if item.get("remote"):
            location = f"{location} (remote)" if location else "Remote"
        jobs.append(Job(
            source="arbeitnow",
            company=item.get("company_name", ""),
            title=item.get("title", ""),
            location=location,
            url=item.get("url", ""),
        ))
    return jobs


def fetch() -> List[Job]:
    return safe_fetch(
        lambda: parse_arbeitnow(http_get_json(API)),
        "arbeitnow"
    )
