"""YCombinator (Work at a Startup) — Algolia search API. Free, no key needed."""
from typing import List
from models import Job, make_id
from sources.base import safe_fetch

import requests
import logging

log = logging.getLogger("qa-radar")

ALGOLIA_URL = "https://45bwzj1sgc-dsn.algolia.net/1/indexes/WaaSJobs_production/query"
ALGOLIA_APP_ID = "45BWZJ1SGC"
ALGOLIA_API_KEY = "MjBjYjRiMzY0NzdhZWY0NjExY2NhZjYxMGIxYjc2MTAwNWFkNTkwNTc4NjgxYjU0YzFhYTY2ZGQ5OGY5NDMzZnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJXYWFTSm9ic19wcm9kdWN0aW9uJTIyJTVEJnRhZ0ZpbHRlcnM9JTVCJTIyaGlyaW5nX3N0YWdlJTNBYWN0aXZlJTIyJTVEJmFuYWx5dGljc1RhZ3M9JTVCJTIyd2Fhcl9qb2JzX3NlYXJjaCUyMiU1RA=="


def parse_yc(hits: list) -> List[Job]:
    jobs = []
    for hit in hits:
        company = hit.get("company_name", "")
        title = hit.get("title", "")
        location = hit.get("location", "")
        url = hit.get("url", "")
        if not url and hit.get("slug"):
            url = f"https://www.workatastartup.com/jobs/{hit['slug']}"
        jobs.append(Job(
            source="ycombinator",
            company=company,
            title=title,
            location=location,
            url=url,
            posted_at=None,
            id=make_id("ycombinator", company, title, url),
        ))
    return jobs


def fetch(queries: List[str] = None) -> List[Job]:
    """Search YC jobs via Algolia. Queries default to SDET-related terms."""
    if queries is None:
        queries = ["sdet", "test automation", "quality engineer", "automation engineer"]

    all_jobs: List[Job] = []

    for query in queries:
        def _fetch(q=query):
            headers = {
                "X-Algolia-Application-Id": ALGOLIA_APP_ID,
                "X-Algolia-API-Key": ALGOLIA_API_KEY,
                "Content-Type": "application/json",
            }
            payload = {
                "query": q,
                "hitsPerPage": 50,
                "filters": "hiring_stage:active",
            }
            r = requests.post(ALGOLIA_URL, headers=headers, json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            return parse_yc(data.get("hits", []))

        all_jobs += safe_fetch(_fetch, f"ycombinator/{query}")

    # Deduplicate by ID
    seen_ids = set()
    unique = []
    for j in all_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            unique.append(j)
    return unique
