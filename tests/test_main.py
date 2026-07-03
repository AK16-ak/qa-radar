from models import Job
from main import select_new


def _job(title, location="Remote", url="https://example.com"):
    return Job(source="test", company="TestCo", title=title,
               location=location, url=url)


CFG = {
    "include_keywords": ["sdet", "test automation", "automation tester"],
    "exclude_keywords": ["intern", "staff", "director"],
    "allowed_locations": ["bengaluru", "pune", "remote", "hyderabad",
                          "gurugram", "delhi", "noida"],
    "strict_location": True,
}


def test_select_new_filters():
    jobs = [_job("SDET"), _job("Backend Developer"), _job("Test Automation Engineer")]
    result = select_new(jobs, CFG, set())
    titles = [j.title for j, _ in result]
    assert "SDET" in titles
    assert "Test Automation Engineer" in titles
    assert "Backend Developer" not in titles


def test_select_new_excludes():
    jobs = [_job("Staff SDET"), _job("SDET Intern")]
    result = select_new(jobs, CFG, set())
    assert len(result) == 0


def test_select_new_respects_seen():
    j = _job("SDET")
    result = select_new([j], CFG, {j.id})
    assert len(result) == 0


def test_select_new_priority_flag():
    jobs = [_job("SDET", "Bengaluru"), _job("Test Automation Engineer", "Pune")]
    result = select_new(jobs, CFG, set())
    for job, priority in result:
        assert priority is True  # both are in allowed_locations


def test_select_new_rejects_non_india():
    jobs = [_job("SDET", "San Francisco")]
    result = select_new(jobs, CFG, set())
    assert len(result) == 0
