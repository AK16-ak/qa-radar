from sources.adzuna import parse_adzuna
from sources.remotive import parse_remotive


def test_parse_adzuna():
    data = {"results": [{
        "id": 12345,
        "company": {"display_name": "AdzCo"},
        "title": "SDET - Automation",
        "location": {"display_name": "Bengaluru"},
        "redirect_url": "https://adzuna.in/j/1",
        "created": "2026-06-28",
        "salary_min": 1800000,
    }]}
    jobs = parse_adzuna(data)
    assert len(jobs) == 1
    assert jobs[0].title == "SDET - Automation"
    assert jobs[0].salary is not None
    assert "1,800,000" in jobs[0].salary


def test_parse_adzuna_stable_id():
    data = {"results": [{
        "id": 99999,
        "company": {"display_name": "Foo"},
        "title": "QA Engineer",
        "location": {"display_name": "Mumbai"},
        "redirect_url": "https://adzuna.in/rotate/1",
        "created": "2026-06-28",
    }]}
    jobs1 = parse_adzuna(data)
    data["results"][0]["redirect_url"] = "https://adzuna.in/rotate/2"
    jobs2 = parse_adzuna(data)
    # ID should be stable regardless of rotating redirect_url
    assert jobs1[0].id == jobs2[0].id


def test_parse_remotive():
    data = {"jobs": [{
        "company_name": "RemCo",
        "title": "Test Automation Engineer",
        "candidate_required_location": "Anywhere",
        "url": "https://remotive.com/j/1",
    }]}
    jobs = parse_remotive(data)
    assert len(jobs) == 1
    assert jobs[0].title == "Test Automation Engineer"
    assert jobs[0].source == "remotive"
