from typing import List
from models import Job, make_id
from sources.base import http_get_json, safe_fetch

API = "https://himalayas.app/jobs/api"


def parse_himalayas(data: dict) -> List[Job]:
    jobs = []
    for item in data.get("jobs", []):
        loc_list = item.get("locationRestrictions") or []
        location = ", ".join(loc_list) if loc_list else "Remote"
        guid = item.get("guid", "")
        company = item.get("companyName", "")
        title = item.get("title", "")
        jobs.append(Job(
            source="himalayas",
            company=company,
            title=title,
            location=location,
            url=item.get("applicationUrl") or item.get("url", ""),
            id=make_id("himalayas", company, title, f"hm-guid:{guid}") if guid else "",
        ))
    return jobs


def fetch(limit: int = 50) -> List[Job]:
    return safe_fetch(
        lambda: parse_himalayas(http_get_json(API, params={"limit": limit})),
        "himalayas"
    )
