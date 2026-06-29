from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://remotive.com/api/remote-jobs"


def parse_remotive(data: dict) -> List[Job]:
    jobs = []
    for item in data.get("jobs", []):
        jobs.append(Job(
            source="remotive",
            company=item.get("company_name", ""),
            title=item.get("title", ""),
            location=item.get("candidate_required_location", ""),
            url=item.get("url", ""),
        ))
    return jobs


def fetch(search: str = "qa") -> List[Job]:
    return safe_fetch(
        lambda: parse_remotive(http_get_json(API, params={"search": search})),
        "remotive"
    )
