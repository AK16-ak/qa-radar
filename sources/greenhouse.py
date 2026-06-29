from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://boards-api.greenhouse.io/v1/boards/{}/jobs"


def parse_greenhouse(data: dict, company: str) -> List[Job]:
    jobs = []
    for item in data.get("jobs", []):
        jobs.append(Job(
            source="greenhouse",
            company=company,
            title=item.get("title", ""),
            location=(item.get("location") or {}).get("name", ""),
            url=item.get("absolute_url", ""),
            posted_at=item.get("updated_at"),
        ))
    return jobs


def fetch(company: str) -> List[Job]:
    return safe_fetch(
        lambda: parse_greenhouse(http_get_json(API.format(company)), company),
        f"greenhouse/{company}"
    )
