"""Google Careers — Public careers API. Free, no key needed."""
from typing import List
from models import Job, make_id
from sources.base import safe_fetch

import requests
import logging

log = logging.getLogger("qa-radar")

# Google Careers uses a public API endpoint
CAREERS_URL = "https://careers.google.com/api/v3/search/"


def parse_google(jobs_data: list) -> List[Job]:
    jobs = []
    for item in jobs_data:
        job_info = item.get("job", {})
        title = job_info.get("title", "")
        company = "Google"

        # Location parsing
        locations = job_info.get("locations", [])
        location = ", ".join(
            loc.get("display", "") for loc in locations
        ) if locations else ""

        # URL
        job_id = job_info.get("id", "")
        url = f"https://www.google.com/about/careers/applications/jobs/results/{job_id}" if job_id else ""

        # Posted date
        publish_date = job_info.get("publish_date", {})
        posted_at = None
        if publish_date:
            y = publish_date.get("year", "")
            m = publish_date.get("month", "")
            d = publish_date.get("day", "")
            if y and m and d:
                posted_at = f"{y}-{m:02d}-{d:02d}" if isinstance(m, int) else f"{y}-{m}-{d}"

        jobs.append(Job(
            source="google",
            company=company,
            title=title,
            location=location,
            url=url,
            posted_at=posted_at,
            id=make_id("google", company, title, url),
        ))
    return jobs


def fetch(queries: List[str] = None, location: str = "India") -> List[Job]:
    """Search Google Careers for QA/SDET roles."""
    if queries is None:
        queries = ["sdet", "test automation", "software engineer in test", "quality engineer"]

    all_jobs: List[Job] = []

    for query in queries:
        def _fetch(q=query):
            params = {
                "q": q,
                "location": location,
                "page_size": 20,
            }
            headers = {"User-Agent": "qa-radar/1.0"}
            r = requests.get(CAREERS_URL, params=params, headers=headers, timeout=20)
            r.raise_for_status()
            data = r.json()
            return parse_google(data.get("jobs", []))

        all_jobs += safe_fetch(_fetch, f"google/{query}")

    # Deduplicate
    seen_ids = set()
    unique = []
    for j in all_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            unique.append(j)
    return unique
