from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://api.lever.co/v0/postings/{}?mode=json"


def parse_lever(data: list, company: str) -> List[Job]:
    jobs = []
    for item in data or []:
        jobs.append(Job(
            source="lever",
            company=company,
            title=item.get("text", ""),
            location=(item.get("categories") or {}).get("location", ""),
            url=item.get("hostedUrl", ""),
        ))
    return jobs


def fetch(company: str) -> List[Job]:
    return safe_fetch(
        lambda: parse_lever(http_get_json(API.format(company)), company),
        f"lever/{company}"
    )
