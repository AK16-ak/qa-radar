from models import Job
from filters import matches, is_priority, _is_india_or_remote

CFG = {
    "include_keywords": ["sdet", "test automation", "automation engineer",
                         "automation tester", "selenium", "cypress",
                         "playwright", "appium"],
    "exclude_keywords": ["senior staff", "staff", "principal", "intern",
                         "director", "manager", "frontend developer"],
    "allowed_locations": ["gurugram", "gurgaon", "pune", "hyderabad",
                          "bengaluru", "bangalore", "delhi", "new delhi",
                          "noida", "remote"],
    "strict_location": True,
}


def _job(title, location=""):
    return Job(source="test", company="Acme", title=title,
               location=location, url="https://example.com")


# --- Title keyword tests ---

def test_include_match():
    assert matches(_job("SDET - Platform", "Pune"), CFG)
    assert matches(_job("Test Automation Engineer", "Remote"), CFG)
    assert matches(_job("Selenium Automation Engineer", "Bengaluru"), CFG)


def test_exclude_rejects():
    assert not matches(_job("Staff SDET", "Pune"), CFG)
    assert not matches(_job("SDET Intern", "Delhi"), CFG)
    assert not matches(_job("Director of Automation", "Noida"), CFG)


def test_no_keyword_rejects():
    assert not matches(_job("Backend Developer", "Pune"), CFG)
    assert not matches(_job("Product Manager", "Bengaluru"), CFG)
    assert not matches(_job("QA Engineer", "Hyderabad"), CFG)  # generic QA excluded


def test_word_boundary():
    assert not matches(_job("Sdetail Engineer", "Remote"), CFG)
    assert matches(_job("Selenium Automation Engineer", "Gurugram"), CFG)


# --- Location filter tests ---

def test_allowed_indian_cities_pass():
    for city in ["Gurugram", "Pune", "Hyderabad", "Bengaluru, India",
                 "Delhi", "New Delhi", "Noida, UP"]:
        assert matches(_job("SDET", city), CFG), f"should pass for {city}"


def test_remote_passes():
    assert matches(_job("SDET", "Remote"), CFG)
    assert matches(_job("SDET", "Anywhere"), CFG)
    assert matches(_job("SDET", "Worldwide"), CFG)
    assert matches(_job("SDET", "Work from home"), CFG)


def test_india_in_location_passes():
    assert matches(_job("SDET", "Mumbai, India"), CFG)
    assert matches(_job("SDET", "India - Kolkata"), CFG)


def test_non_india_rejected():
    assert not matches(_job("SDET", "San Francisco, CA"), CFG)
    assert not matches(_job("SDET", "New York, US"), CFG)
    assert not matches(_job("SDET", "London, UK"), CFG)
    assert not matches(_job("SDET", "Berlin, Germany"), CFG)


def test_empty_location_passes():
    assert matches(_job("SDET", ""), CFG)
    assert matches(_job("SDET"), CFG)


def test_priority_location():
    assert is_priority(_job("SDET", "Bengaluru, India"), CFG)
    assert is_priority(_job("SDET", "Remote"), CFG)
    assert not is_priority(_job("SDET", "Mumbai, India"), CFG)  # not in allowed list


# --- Strict mode off ---

def test_non_strict_allows_all():
    loose_cfg = {**CFG, "strict_location": False}
    assert matches(_job("SDET", "San Francisco"), loose_cfg)
