"""Workday — Public job search API per company. Free, no key needed.
Major companies using Workday: Amazon, Microsoft, Infosys, Wipro, TCS, etc."""
from typing import List, Dict
from models import Job, make_id
from sources.base import safe_fetch

import requests
import logging

log = logging.getLogger("qa-radar")

# Workday career sites follow this pattern:
# https://{tenant}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
# Search endpoint: POST to the jobs URL with filters


def parse_workday(data: dict, company: str) -> List[Job]:
    jobs = []
    for item in data.get("jobPostings", []):
        title = item.get("title", "")
        location = item.get("locationsText", "") or item.get("bulletFields", [""])[0]
        external_path = item.get("externalPath", "")
        url = ""
        if external_path:
            url = external_path  # Will be prefixed by caller
        posted = item.get("postedOn", "")

        jobs.append(Job(
            source="workday",
            company=company,
            title=title,
            location=location,
            url=url,
            posted_at=posted or None,
            id=make_id("workday", company, title, external_path),
        ))
    return jobs


def fetch_company(tenant: str, site: str, company_name: str,
                  wd_version: int = 5, queries: List[str] = None) -> List[Job]:
    """Fetch jobs from a single Workday company career site."""
    if queries is None:
        queries = ["sdet", "test automation", "quality engineer"]

    base_url = f"https://{tenant}.wd{wd_version}.myworkdayjobs.com"
    search_url = f"{base_url}/wday/cxs/{tenant}/{site}/jobs"

    all_jobs: List[Job] = []

    for query in queries:
        def _fetch(q=query):
            payload = {
                "appliedFacets": {},
                "limit": 20,
                "offset": 0,
                "searchText": q,
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "qa-radar/1.0",
            }
            r = requests.post(search_url, headers=headers, json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            jobs = parse_workday(data, company_name)
            # Fix URLs with base
            for j in jobs:
                if j.url and not j.url.startswith("http"):
                    j.url = f"{base_url}/en-US{j.url}"
            return jobs

        all_jobs += safe_fetch(_fetch, f"workday/{company_name}/{query}")

    # Deduplicate
    seen_ids = set()
    unique = []
    for j in all_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            unique.append(j)
    return unique


def fetch(companies: List[Dict]) -> List[Job]:
    """Fetch from multiple Workday companies.
    Each company dict: {name, tenant, site, wd_version (optional, default 5)}
    """
    all_jobs: List[Job] = []
    for company in companies:
        jobs = fetch_company(
            tenant=company["tenant"],
            site=company["site"],
            company_name=company["name"],
            wd_version=company.get("wd_version", 5),
            queries=company.get("queries"),
        )
        all_jobs += jobs
    return all_jobs
