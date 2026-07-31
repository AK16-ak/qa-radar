from ats.scorer import calculate_ats_score


def test_perfect_score():
    jd_kw = {"java", "selenium", "testng"}
    resume_kw = {"java", "selenium", "testng", "jenkins"}
    result = calculate_ats_score(resume_kw, jd_kw, "SDET", "SDET with experience")
    assert result["score"] >= 90
    assert result["missing"] == []
    assert set(result["matched"]) == {"java", "selenium", "testng"}


def test_partial_score():
    jd_kw = {"java", "selenium", "testng", "docker", "kubernetes", "cypress"}
    resume_kw = {"java", "selenium", "testng"}
    result = calculate_ats_score(resume_kw, jd_kw, "SDET", "SDET with experience")
    assert result["score"] < 90
    assert "docker" in result["missing"]
    assert "java" in result["matched"]


def test_empty_jd_keywords():
    result = calculate_ats_score({"java", "selenium"}, set(), "SDET", "SDET summary")
    assert result["score"] == 85  # default when no JD keywords


def test_score_structure():
    jd_kw = {"java", "selenium"}
    resume_kw = {"java"}
    result = calculate_ats_score(resume_kw, jd_kw, "SDET", "SDET")
    assert "score" in result
    assert "matched" in result
    assert "missing" in result
    assert "breakdown" in result
    assert "keyword_match" in result["breakdown"]
