from sources.greenhouse import parse_greenhouse
from sources.lever import parse_lever
from sources.ashby import parse_ashby


def test_parse_greenhouse():
    data = {"jobs": [{
        "title": "SDET - Platform",
        "location": {"name": "Bengaluru, India"},
        "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
        "updated_at": "2026-06-28T10:00:00Z",
    }]}
    jobs = parse_greenhouse(data, "acme")
    assert len(jobs) == 1
    assert jobs[0].title == "SDET - Platform"
    assert jobs[0].company == "acme"
    assert jobs[0].source == "greenhouse"
    assert "Bengaluru" in jobs[0].location


def test_parse_lever():
    data = [{
        "text": "QA Automation Engineer",
        "hostedUrl": "https://jobs.lever.co/acme/456",
        "categories": {"location": "Remote"},
    }]
    jobs = parse_lever(data, "acme")
    assert len(jobs) == 1
    assert jobs[0].title == "QA Automation Engineer"
    assert jobs[0].source == "lever"
    assert jobs[0].location == "Remote"


def test_parse_ashby():
    data = {"jobs": [{
        "title": "Senior SDET",
        "location": "Hyderabad, India",
        "jobUrl": "https://jobs.ashbyhq.com/acme/789",
    }]}
    jobs = parse_ashby(data, "acme")
    assert len(jobs) == 1
    assert jobs[0].title == "Senior SDET"
    assert jobs[0].source == "ashby"
    assert "Hyderabad" in jobs[0].location
