from models import Job
from main import select_new


def _job(title, location="Remote", url="https://example.com"):
    return Job(source="test", company="TestCo", title=title,
               location=location, url=url)


CFG = {
    "include_keywords": ["sdet", "qa engineer", "test automation", "qa"],
    "exclude_keywords": ["intern", "staff", "director"],
    "priority_locations": ["bengaluru", "remote"],
    "strict_location": False,
}


def test_select_new_filters():
    jobs = [_job("SDET"), _job("Backend Developer"), _job("QA Engineer")]
    result = select_new(jobs, CFG, set())
    titles = [j.title for j, _ in result]
    assert "SDET" in titles
    assert "QA Engineer" in titles
    assert "Backend Developer" not in titles


def test_select_new_excludes():
    jobs = [_job("Staff SDET"), _job("QA Intern")]
    result = select_new(jobs, CFG, set())
    assert len(result) == 0


def test_select_new_respects_seen():
    j = _job("SDET")
    result = select_new([j], CFG, {j.id})
    assert len(result) == 0


def test_select_new_priority_flag():
    jobs = [_job("SDET", "Bengaluru"), _job("QA Engineer", "San Francisco")]
    result = select_new(jobs, CFG, set())
    for job, priority in result:
        if job.location == "Bengaluru":
            assert priority is True
        else:
            assert priority is False
