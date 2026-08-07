"""LinkedIn Jobs via RapidAPI — Free tier (5-10 req/month). Needs RAPIDAPI_KEY secret.
If key not set or rate limited, gracefully returns empty list."""
from typing import List
from models import Job, make_id
from sources.base import safe_fetch

import requests
import logging

log = logging.getLogger("qa-radar")

RAPIDAPI_HOST = "linkedin-jobs-search.p.rapidapi.com"
RAPIDAPI_URL = f"https://{RAPIDAPI_HOST}/"


def parse_linkedin(items: list) -> List[Job]:
    jobs = []
    for item in items:
        title = item.get("job_title", "")
        company = item.get("company_name", "")
        location = item.get("job_location", "")
        url = item.get("linkedin_job_url_cleaned", "") or item.get("job_url", "")
        posted = item.get("posted_date", "")

        jobs.append(Job(
            source="linkedin",
            company=company,
            title=title,
            location=location,
            url=url,
            posted_at=posted or None,
            id=make_id("linkedin", company, title, url),
        ))
    return jobs


def fetch(api_key: str, queries: List[str] = None, location: str = "India") -> List[Job]:
    """Search LinkedIn jobs via RapidAPI. Returns empty if no key or rate limited."""
    if not api_key:
        return []

    if queries is None:
        queries = ["sdet india", "test automation engineer india"]

    all_jobs: List[Job] = []

    for query in queries:
        def _fetch(q=query):
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": RAPIDAPI_HOST,
                "Content-Type": "application/json",
            }
            payload = {
                "search_terms": q,
                "location": location,
                "page": "1",
            }
            r = requests.post(RAPIDAPI_URL, headers=headers, json=payload, timeout=30)
            if r.status_code == 429:
                log.info("linkedin: rate limited (free tier exhausted), skipping")
                return []
            if r.status_code == 403:
                log.info("linkedin: forbidden (check API key), skipping")
                return []
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list):
                return parse_linkedin(data)
            return parse_linkedin(data.get("results", data.get("jobs", [])))

        all_jobs += safe_fetch(_fetch, f"linkedin/{query}")

    # Deduplicate
    seen_ids = set()
    unique = []
    for j in all_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            unique.append(j)
    return unique
