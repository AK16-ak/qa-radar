from models import Job
from filters import matches, is_priority

CFG = {
    "include_keywords": ["sdet", "qa", "qa engineer", "test automation",
                         "automation engineer", "quality assurance", "selenium"],
    "exclude_keywords": ["senior staff", "staff", "principal", "intern",
                         "director", "manager", "frontend developer"],
    "priority_locations": ["bengaluru", "bangalore", "remote", "hyderabad"],
    "strict_location": False,
}


def _job(title, location=""):
    return Job(source="test", company="Acme", title=title,
               location=location, url="https://example.com")


def test_include_match():
    assert matches(_job("SDET - Platform"), CFG)
    assert matches(_job("QA Automation Engineer"), CFG)
    assert matches(_job("Senior Test Automation Engineer"), CFG)


def test_exclude_rejects():
    assert not matches(_job("Staff SDET"), CFG)
    assert not matches(_job("QA Intern"), CFG)
    assert not matches(_job("Director of QA"), CFG)


def test_no_keyword_rejects():
    assert not matches(_job("Backend Developer"), CFG)
    assert not matches(_job("Product Manager"), CFG)


def test_word_boundary():
    # "qa" should not match inside "aqua"
    assert not matches(_job("Aquatic Engineer"), CFG)
    # "selenium" should match standalone
    assert matches(_job("Selenium Automation Engineer"), CFG)


def test_priority_location():
    assert is_priority(_job("SDET", "Bengaluru, India"), CFG)
    assert is_priority(_job("SDET", "Remote"), CFG)
    assert not is_priority(_job("SDET", "San Francisco"), CFG)


def test_strict_location():
    strict_cfg = {**CFG, "strict_location": True}
    assert matches(_job("SDET", "Bengaluru"), strict_cfg)
    assert not matches(_job("SDET", "San Francisco"), strict_cfg)
