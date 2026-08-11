"""Bright Data SERP API — Google Jobs search. Free tier: 5,000 req/month.
Needs BRIGHTDATA_API_KEY and BRIGHTDATA_ZONE as GitHub Secrets.
If not set, gracefully skipped."""
from typing import List
from models import Job, make_id
from sources.base import safe_fetch

import requests
import logging
import json

log = logging.getLogger("qa-radar")

API_URL = "https://api.brightdata.com/request"


def parse_google_jobs(html_or_json, query: str) -> List[Job]:
    """Parse Google Jobs results from Bright Data SERP response.
    Response can be JSON (brd_json=1) or raw HTML."""
    jobs = []

    # If response is JSON (parsed by Bright Data)
    if isinstance(html_or_json, dict):
        # Google Jobs results appear in 'jobs' or 'jobs_results' key
        job_results = (html_or_json.get("jobs")
                       or html_or_json.get("jobs_results")
                       or html_or_json.get("organic")
                       or [])

        for item in job_results:
            title = item.get("title", "")
            company = item.get("company_name", "") or item.get("company", "")
            location = item.get("location", "")
            url = item.get("link", "") or item.get("url", "")
            posted = item.get("detected_extensions", {}).get("posted_at", "")
            salary = item.get("detected_extensions", {}).get("salary", "")

            # Some formats nest differently
            if not company and item.get("extensions"):
                for ext in item["extensions"]:
                    if isinstance(ext, str) and not company:
                        company = ext
                        break

            if title:
                jobs.append(Job(
                    source="brightdata",
                    company=company,
                    title=title,
                    location=location,
                    url=url,
                    posted_at=posted or None,
                    salary=salary or None,
                    id=make_id("brightdata", company, title, url or f"bd:{query}:{title}"),
                ))

        # Also check for general organic results that might be job listings
        for item in html_or_json.get("organic", []):
            title_text = item.get("title", "")
            # Skip non-job results
            if any(kw in title_text.lower() for kw in
                   ["sdet", "test", "automation", "quality", "qa"]):
                url = item.get("link", "")
                desc = item.get("description", "")
                if url and title_text:
                    jobs.append(Job(
                        source="brightdata",
                        company="",
                        title=title_text,
                        location="India",
                        url=url,
                        id=make_id("brightdata", "", title_text, url),
                    ))

    return jobs


def fetch(api_key: str, zone: str, queries: List[str] = None,
          country: str = "in", max_queries_per_run: int = 5) -> List[Job]:
    """Search Google Jobs via Bright Data SERP API.
    Rotates through queries using time-based selection to maximize
    coverage within free tier limits (5,000 req/month).
    """
    if not api_key or not zone:
        return []

    if queries is None:
        queries = [
            "sdet india",
            "test automation engineer india",
            "automation tester india",
        ]

    # Rotate: pick a subset of queries per run based on current hour
    # This distributes all queries across the day evenly
    import time
    current_slot = int(time.time() // 1200) % len(queries)  # 20-min slots
    selected = []
    for i in range(max_queries_per_run):
        idx = (current_slot + i) % len(queries)
        if queries[idx] not in selected:
            selected.append(queries[idx])
    log.info("brightdata: running %d/%d queries this slot", len(selected), len(queries))

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    all_jobs: List[Job] = []

    for query in selected:
        def _fetch(q=query):
            # Google Jobs URL: use ibp=htl;jobs for jobs search
            search_q = q.replace(" ", "+")
            google_url = (
                f"https://www.google.com/search?"
                f"q={search_q}&ibp=htl%3Bjobs&hl=en&gl={country}"
            )

            payload = {
                "zone": zone,
                "url": google_url,
                "format": "raw",
                "brd_json": "1",
            }

            r = requests.post(API_URL, headers=headers, json=payload, timeout=60)

            if r.status_code == 401:
                log.warning("brightdata: auth failed — check API key & zone")
                return []
            if r.status_code == 429:
                log.warning("brightdata: rate limited, skipping")
                return []

            r.raise_for_status()

            try:
                data = r.json()
            except (json.JSONDecodeError, ValueError):
                log.warning("brightdata: non-JSON response for query '%s'", q)
                return []

            return parse_google_jobs(data, q)

        all_jobs += safe_fetch(_fetch, f"brightdata/{query}")

    # Deduplicate
    seen_ids = set()
    unique = []
    for j in all_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            unique.append(j)

    log.info("brightdata: %d unique jobs from %d queries", len(unique), len(queries))
    return unique
