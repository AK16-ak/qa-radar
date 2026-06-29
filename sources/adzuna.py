from typing import List
from models import Job, make_id
from sources.base import http_get_json, safe_fetch

API = "https://api.adzuna.com/v1/api/jobs/{}/search/1"


def parse_adzuna(data: dict) -> List[Job]:
    jobs = []
    for item in data.get("results", []):
        salary = ""
        if item.get("salary_min"):
            salary = f"₹{int(item['salary_min']):,}+"
        aid = str(item.get("id", ""))
        company = (item.get("company") or {}).get("display_name", "")
        title = item.get("title", "")
        jobs.append(Job(
            source="adzuna",
            company=company,
            title=title,
            location=(item.get("location") or {}).get("display_name", ""),
            url=item.get("redirect_url", ""),
            posted_at=item.get("created"),
            salary=salary or None,
            id=make_id("adzuna", company, title, f"adzuna-id:{aid}"),
        ))
    return jobs


def fetch(app_id, app_key, queries, country="in") -> List[Job]:
    if not app_id or not app_key:
        return []
    jobs: List[Job] = []
    for q in queries:
        def _fetch(query=q):
            data = http_get_json(API.format(country), params={
                "app_id": app_id, "app_key": app_key,
                "what": query, "results_per_page": 50,
                "max_days_old": 3, "sort_by": "date",
            })
            return parse_adzuna(data)
        jobs += safe_fetch(_fetch, f"adzuna/{q}")
    return jobs
