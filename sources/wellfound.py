"""Wellfound (formerly AngelList Talent) — GraphQL public endpoint. Free, no key."""
from typing import List
from models import Job, make_id
from sources.base import safe_fetch

import requests
import logging

log = logging.getLogger("qa-radar")

GRAPHQL_URL = "https://wellfound.com/graphql"


def parse_wellfound(edges: list) -> List[Job]:
    jobs = []
    for edge in edges:
        node = edge.get("node", {})
        company_node = node.get("startup", {}) or {}
        company = company_node.get("name", "")
        title = node.get("title", "")
        location = node.get("locationNames", "")
        if isinstance(location, list):
            location = ", ".join(location)

        slug = node.get("slug", "")
        url = f"https://wellfound.com/jobs/{slug}" if slug else ""

        salary = ""
        if node.get("compensation"):
            salary = node["compensation"]

        jobs.append(Job(
            source="wellfound",
            company=company,
            title=title,
            location=location,
            url=url,
            posted_at=node.get("postedAt"),
            salary=salary or None,
            id=make_id("wellfound", company, title, url),
        ))
    return jobs


def fetch(queries: List[str] = None) -> List[Job]:
    """Search Wellfound jobs via their public GraphQL endpoint."""
    if queries is None:
        queries = ["sdet", "test automation", "quality engineer"]

    all_jobs: List[Job] = []

    for query in queries:
        def _fetch(q=query):
            payload = {
                "operationName": "JobSearchResultsQuery",
                "variables": {
                    "query": q,
                    "page": 1,
                    "perPage": 50,
                    "locationTags": ["india"],
                },
                "query": """
                    query JobSearchResultsQuery($query: String, $page: Int, $perPage: Int, $locationTags: [String]) {
                        talent {
                            jobListings(
                                filters: {
                                    query: $query
                                    locationTags: $locationTags
                                }
                                page: $page
                                perPage: $perPage
                            ) {
                                edges {
                                    node {
                                        title
                                        slug
                                        locationNames
                                        postedAt
                                        compensation
                                        startup {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                """,
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "qa-radar/1.0",
            }
            r = requests.post(GRAPHQL_URL, headers=headers, json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            edges = (data.get("data", {}).get("talent", {})
                     .get("jobListings", {}).get("edges", []))
            return parse_wellfound(edges)

        all_jobs += safe_fetch(_fetch, f"wellfound/{query}")

    # Deduplicate
    seen_ids = set()
    unique = []
    for j in all_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            unique.append(j)
    return unique
