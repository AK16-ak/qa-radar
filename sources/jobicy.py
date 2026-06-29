from typing import List, Optional
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://jobicy.com/api/v2/remote-jobs"


def parse_jobicy(data: dict) -> List[Job]:
    jobs = []
    for item in data.get("jobs", []):
        jobs.append(Job(
            source="jobicy",
            company=item.get("companyName", ""),
            title=item.get("jobTitle", ""),
            location=item.get("jobGeo", ""),
            url=item.get("url", ""),
            posted_at=item.get("pubDate"),
        ))
    return jobs


def fetch(tags: Optional[List[str]] = None) -> List[Job]:
    tags = tags or ["qa"]
    jobs: List[Job] = []
    for tag in tags:
        def _fetch(t=tag):
            return parse_jobicy(http_get_json(API, params={"tag": t}))
        jobs += safe_fetch(_fetch, f"jobicy/{tag}")
    return jobs
