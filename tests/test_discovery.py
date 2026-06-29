from sources.remoteok import parse_remoteok
from sources.arbeitnow import parse_arbeitnow
from sources.himalayas import parse_himalayas
from sources.jobicy import parse_jobicy
from sources.smartrecruiters import parse_smartrecruiters
from sources.themuse import parse_themuse


def test_parse_remoteok():
    data = [
        {"legal": "metadata"},
        {"company": "TestCo", "position": "QA Automation Engineer",
         "location": "Remote", "url": "https://remoteok.com/l/1", "date": "2026-06-28"},
    ]
    jobs = parse_remoteok(data)
    assert len(jobs) == 1
    assert jobs[0].title == "QA Automation Engineer"
    assert jobs[0].source == "remoteok"


def test_parse_arbeitnow():
    data = {"data": [{
        "company_name": "QualityCo",
        "title": "Test Automation Engineer",
        "location": "Berlin",
        "url": "https://arbeitnow.com/j/1",
        "remote": True,
    }]}
    jobs = parse_arbeitnow(data)
    assert len(jobs) == 1
    assert "(remote)" in jobs[0].location
    assert jobs[0].source == "arbeitnow"


def test_parse_himalayas():
    data = {"jobs": [{
        "companyName": "HimalCo",
        "title": "SDET",
        "locationRestrictions": ["India", "Remote"],
        "url": "https://himalayas.app/j/1",
        "applicationUrl": "https://apply.com/1",
        "guid": "abc-123",
    }]}
    jobs = parse_himalayas(data)
    assert len(jobs) == 1
    assert jobs[0].company == "HimalCo"
    assert "India" in jobs[0].location


def test_parse_jobicy():
    data = {"jobs": [{
        "companyName": "JobCo",
        "jobTitle": "QA Engineer",
        "jobGeo": "Worldwide",
        "url": "https://jobicy.com/j/1",
        "pubDate": "2026-06-28",
    }]}
    jobs = parse_jobicy(data)
    assert len(jobs) == 1
    assert jobs[0].title == "QA Engineer"
    assert jobs[0].source == "jobicy"


def test_parse_smartrecruiters():
    data = {"content": [{
        "id": "sr-001",
        "name": "SDET II",
        "location": {"fullLocation": "Pune, India", "city": "Pune", "country": "India"},
    }]}
    jobs = parse_smartrecruiters(data, "TestCorp")
    assert len(jobs) == 1
    assert jobs[0].title == "SDET II"
    assert "Pune" in jobs[0].location
    assert jobs[0].source == "smartrecruiters"


def test_parse_themuse():
    data = {"results": [{
        "name": "Quality Assurance Engineer",
        "company": {"name": "MuseCo"},
        "locations": [{"name": "Bengaluru, India"}],
        "refs": {"landing_page": "https://themuse.com/j/1"},
        "publication_date": "2026-06-28",
    }]}
    jobs = parse_themuse(data)
    assert len(jobs) == 1
    assert jobs[0].title == "Quality Assurance Engineer"
    assert jobs[0].source == "themuse"
