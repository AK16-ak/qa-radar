from ats.jd_parser import extract_experience, experience_matches


def test_extract_range():
    assert extract_experience("Looking for 3-5 years of experience") == (3, 5)
    assert extract_experience("Need 2 to 4 years experience") == (2, 4)


def test_extract_plus():
    assert extract_experience("5+ years of experience in testing") == (5, None)
    assert extract_experience("Must have 3+ yrs experience") == (3, None)


def test_extract_minimum():
    assert extract_experience("Minimum 4 years of experience") == (4, None)
    assert extract_experience("At least 3 years experience required") == (3, None)


def test_extract_none():
    assert extract_experience("Great opportunity for SDET professionals") == (None, None)
    assert extract_experience("") == (None, None)
    assert extract_experience(None) == (None, None)


def test_experience_matches_in_range():
    # my_years=3, max_target=6
    ok, _ = experience_matches("3-5 years experience", 3, 6)
    assert ok is True


def test_experience_matches_plus():
    ok, _ = experience_matches("2+ years experience", 3, 6)
    assert ok is True


def test_experience_too_junior():
    ok, _ = experience_matches("0-2 years experience", 3, 6)
    assert ok is False


def test_experience_too_senior():
    ok, _ = experience_matches("8+ years experience", 3, 6)
    assert ok is False


def test_experience_no_mention():
    ok, _ = experience_matches("Join our team as SDET", 3, 6)
    assert ok is True


def test_experience_stretch_target():
    # Job asks 4-6, you have 3 — it's within max_target so should match
    ok, _ = experience_matches("4-6 years experience required", 3, 6)
    assert ok is True
