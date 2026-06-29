from models import Job, make_id


def test_make_id_stable():
    id1 = make_id("greenhouse", "acme", "SDET", "https://x.com/1")
    id2 = make_id("greenhouse", "acme", "SDET", "https://x.com/1")
    assert id1 == id2


def test_make_id_changes_with_url():
    id1 = make_id("greenhouse", "acme", "SDET", "https://x.com/1")
    id2 = make_id("greenhouse", "acme", "SDET", "https://x.com/2")
    assert id1 != id2


def test_job_auto_id():
    j = Job(source="lever", company="test", title="QA Engineer",
            location="Remote", url="https://example.com/job")
    assert j.id != ""
    assert len(j.id) == 16


def test_job_preserves_explicit_id():
    j = Job(source="lever", company="test", title="QA Engineer",
            location="Remote", url="https://example.com/job", id="custom123")
    assert j.id == "custom123"
