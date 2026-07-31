from ats.keyword_extractor import extract_keywords, get_resume_keywords


def test_extract_keywords_from_jd():
    jd = """
    We are looking for an SDET with experience in Selenium, Java, TestNG,
    and CI/CD. Must have knowledge of API testing, Docker, and Kubernetes.
    Experience with BDD and Cucumber is a plus. Familiarity with Jira and Git.
    """
    keywords = extract_keywords(jd)
    assert "selenium" in keywords
    assert "java" in keywords
    assert "testng" in keywords
    assert "ci/cd" in keywords
    assert "docker" in keywords
    assert "kubernetes" in keywords
    assert "bdd" in keywords
    assert "cucumber" in keywords
    assert "jira" in keywords
    assert "git" in keywords
    assert "api testing" in keywords


def test_extract_empty():
    assert extract_keywords("") == set()
    assert extract_keywords(None) == set()


def test_get_resume_keywords():
    resume = {
        "summary": "SDET with experience in Java and Selenium",
        "skills": {
            "frameworks": ["Selenium", "TestNG", "Rest Assured"],
            "tools": ["Jenkins", "Jira"],
        },
        "experience": [
            {"bullets": ["Built automation using Java and TestNG"]}
        ],
        "projects": [
            {"bullets": ["Used Selenium with POM pattern"]}
        ],
    }
    keywords = get_resume_keywords(resume)
    assert "selenium" in keywords
    assert "java" in keywords
    assert "testng" in keywords
    assert "jenkins" in keywords
    assert "jira" in keywords
    assert "pom" in keywords
