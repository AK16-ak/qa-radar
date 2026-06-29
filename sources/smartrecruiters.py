from typing import List
from models import Job, make_id
from sources.base import http_get_json, safe_fetch

API = "https://api.smartrecruiters.com/v1/companies/{}/postings"


def parse_smartrecruiters(data: dict, company: str) -> List[Job]:
    jobs = []
    for item in data.get("content", []):
        jid = item.get("id", "")
        loc = item.get("location") or {}
        location = loc.get("fullLocation") or ""
        if not location:
            city = loc.get("city", "")
            country = loc.get("country", "")
            location = f"{city}, {country}".strip(", ")
        url = f"https://jobs.smartrecruiters.com/{company}/{jid}"
        jobs.append(Job(
            source="smartrecruiters",
            company=company,
            title=item.get("name", ""),
            location=location,
            url=url,
            id=make_id("smartrecruiters", company, item.get("name", ""), f"sr-id:{jid}"),
        ))
    return jobs


def fetch(company: str) -> List[Job]:
    return safe_fetch(
        lambda: parse_smartrecruiters(
            http_get_json(API.format(company), params={"limit": 100}), company),
        f"smartrecruiters/{company}"
    )
