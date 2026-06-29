from typing import List, Optional
from models import Job
from sources.base import http_get_json, safe_fetch

API = "https://www.themuse.com/api/public/jobs"


def parse_themuse(data: dict) -> List[Job]:
    jobs = []
    for item in data.get("results", []):
        company = (item.get("company") or {}).get("name", "")
        locs = item.get("locations") or []
        location = ", ".join(loc.get("name", "") for loc in locs)
        jobs.append(Job(
            source="themuse",
            company=company,
            title=item.get("name", ""),
            location=location,
            url=(item.get("refs") or {}).get("landing_page", ""),
            posted_at=item.get("publication_date"),
        ))
    return jobs


def fetch(pages: int = 3, categories: Optional[List[str]] = None,
          locations: Optional[List[str]] = None) -> List[Job]:
    jobs: List[Job] = []
    cats = categories or ["Software Engineering"]
    for cat in cats:
        for page in range(pages):
            def _fetch(c=cat, p=page):
                params = {"category": c, "page": p}
                if locations:
                    params["location"] = locations[0]
                return parse_themuse(http_get_json(API, params=params))
            jobs += safe_fetch(_fetch, f"themuse/{cat}/p{page}")
    return jobs
