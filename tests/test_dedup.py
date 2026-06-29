import os
import json
import tempfile
from models import Job
from dedup import load_seen, save_seen, partition_new


def _job(title, url="https://example.com"):
    return Job(source="test", company="Acme", title=title,
               location="Remote", url=url)


def test_partition_new_filters_seen():
    j1 = _job("SDET", "https://a.com")
    j2 = _job("QA Engineer", "https://b.com")
    seen = {j1.id}
    result = partition_new([j1, j2], seen)
    assert len(result) == 1
    assert result[0].id == j2.id


def test_partition_new_dedupes_within_batch():
    j1 = _job("SDET", "https://a.com")
    result = partition_new([j1, j1], set())
    assert len(result) == 1


def test_save_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "seen.json")
        ids = {"abc123", "def456", "ghi789"}
        save_seen(path, ids)
        loaded = load_seen(path)
        assert loaded == ids


def test_load_missing_file():
    result = load_seen("/nonexistent/path/seen.json")
    assert result == set()


def test_load_corrupt_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not valid json{{{")
        path = f.name
    try:
        result = load_seen(path)
        assert result == set()
    finally:
        os.unlink(path)
