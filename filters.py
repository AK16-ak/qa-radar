import re
from typing import Dict
from models import Job

# Locations that explicitly indicate a non-India role
NON_INDIA_INDICATORS = [
    "united states", "usa", "us only", "u.s.", "canada", "uk only",
    "united kingdom", "europe only", "eu only", "australia",
    "san francisco", "new york", "seattle", "austin", "chicago",
    "boston", "los angeles", "denver", "atlanta", "london", "berlin",
    "paris", "amsterdam", "toronto", "vancouver", "sydney", "tokyo",
    "singapore", "dublin",
]


def _has_kw(text: str, keywords) -> bool:
    text = (text or "").lower()
    for kw in keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, text):
            return True
    return False


def _is_india_or_remote(location: str, cfg: Dict) -> bool:
    """Return True if the job location is in an allowed Indian city or Remote."""
    loc = (location or "").lower().strip()
    if not loc:
        return True  # empty location — benefit of doubt
    allowed = cfg.get("allowed_locations", [])
    if _has_kw(loc, allowed):
        return True
    # "india" anywhere in location string is a pass
    if "india" in loc:
        return True
    # Reject locations that explicitly mention non-India places
    for indicator in NON_INDIA_INDICATORS:
        if indicator in loc:
            return False
    # Generic remote/anywhere/worldwide — accept (could be India-eligible)
    remote_terms = ["remote", "anywhere", "worldwide", "global", "work from home",
                    "wfh", "distributed"]
    for term in remote_terms:
        if term in loc:
            return True
    return False


def matches(job: Job, cfg: Dict) -> bool:
    title = job.title or ""
    if not _has_kw(title, cfg.get("include_keywords", [])):
        return False
    if _has_kw(title, cfg.get("exclude_keywords", [])):
        return False
    if cfg.get("strict_location"):
        return _is_india_or_remote(job.location, cfg)
    return True


def is_priority(job: Job, cfg: Dict) -> bool:
    return _has_kw(job.location or "", cfg.get("allowed_locations", []))
