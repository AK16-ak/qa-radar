from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://api.ashbyhq.com/posting-api/job-board/{}"


def parse_ashby(data: dict, company: str) -> List[Job]:
    jobs = []
    for item in data.get("jobs", []):
        jobs.append(Job(
            source="ashby",
            company=company,
            title=item.get("title", ""),
            location=item.get("location", ""),
            url=item.get("jobUrl", ""),
        ))
    return jobs


def fetch(company: str) -> List[Job]:
    return safe_fetch(
        lambda: parse_ashby(http_get_json(API.format(company)), company),
        f"ashby/{company}"
    )
