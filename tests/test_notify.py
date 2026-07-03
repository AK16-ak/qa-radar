from models import Job
from notify import format_job, format_batch, chunk_messages, send_telegram


def _job(title="SDET", location="Bengaluru", salary=None):
    return Job(source="greenhouse", company="Acme", title=title,
               location=location, url="https://example.com/job", salary=salary)


def test_format_job_basic():
    text = format_job(_job(), priority=False)
    assert "Acme" in text
    assert "SDET" in text
    assert "Bengaluru" in text
    assert "https://example.com/job" in text


def test_format_job_priority_star():
    text = format_job(_job(), priority=True)
    assert "\u2b50" in text


def test_format_job_salary():
    text = format_job(_job(salary="₹18,00,000+"), priority=False)
    assert "₹18,00,000+" in text


def test_format_batch():
    items = [(_job("SDET"), True), (_job("QA Engineer"), False)]
    text = format_batch(items)
    assert "2 new SDET/Automation job(s)" in text
    assert "SDET" in text
    assert "QA Engineer" in text


def test_chunk_messages_splits():
    items = [(_job(f"Job {i}"), False) for i in range(50)]
    chunks = chunk_messages(items, limit=500)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 600  # some slack


def test_send_telegram_success(monkeypatch):
    class FakeResp:
        status_code = 200
    monkeypatch.setattr("notify.requests.post", lambda *a, **kw: FakeResp())
    assert send_telegram("tok", "123", "hello") is True


def test_send_telegram_failure(monkeypatch):
    class FakeResp:
        status_code = 403
        text = "Forbidden"
    monkeypatch.setattr("notify.requests.post", lambda *a, **kw: FakeResp())
    assert send_telegram("tok", "123", "hello") is False


def test_send_telegram_429_retry(monkeypatch):
    calls = []

    class Resp429:
        status_code = 429
        def json(self): return {"parameters": {"retry_after": 1}}

    class Resp200:
        status_code = 200

    def fake_post(*a, **kw):
        calls.append(1)
        return Resp429() if len(calls) <= 2 else Resp200()

    monkeypatch.setattr("notify.requests.post", fake_post)
    monkeypatch.setattr("notify.time.sleep", lambda x: None)
    assert send_telegram("tok", "123", "hello") is True
    assert len(calls) == 3
