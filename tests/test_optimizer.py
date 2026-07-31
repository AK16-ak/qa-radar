from ats.optimizer import optimize_resume


BASE_RESUME = {
    "personal": {"name": "Anubhav Kaushik", "total_experience_years": 3},
    "summary": "SDET with 3 years of experience in test automation.",
    "skills": {
        "programming_languages": ["Java", "Python"],
        "frameworks": ["Selenium", "TestNG"],
        "tools": ["Jenkins", "Jira"],
    },
    "experience": [
        {"role": "SDET", "company": "Cars24", "location": "Gurugram",
         "duration": "Dec 2024 - Jun 2025",
         "bullets": ["Built automation framework using Selenium and Java"]}
    ],
    "projects": [
        {"name": "Airline Test Automation",
         "bullets": ["Used POM pattern with TestNG"]}
    ],
    "education": [{"degree": "B.E. CSE", "institution": "CU", "duration": "2019-2023"}],
    "certifications": ["PCAP Python"],
}


def test_injects_all_jd_keywords():
    jd_keywords = {"docker", "kubernetes", "cypress", "java", "selenium"}
    result = optimize_resume(BASE_RESUME, jd_keywords, "SDET")

    # Gather all skills from result
    all_skills = []
    for category, skills in result["skills"].items():
        all_skills.extend([s.lower() for s in skills])

    assert "docker" in all_skills
    assert "kubernetes" in all_skills
    assert "cypress" in all_skills
    # Existing skills should remain
    assert "java" in all_skills
    assert "selenium" in all_skills


def test_summary_updated():
    jd_keywords = {"java", "selenium", "api testing"}
    result = optimize_resume(BASE_RESUME, jd_keywords, "Test Automation Engineer")
    assert "Test Automation Engineer" in result["summary"]
    assert "3+" in result["summary"]


def test_no_duplicate_skills():
    jd_keywords = {"java", "selenium", "jenkins"}  # all already exist
    result = optimize_resume(BASE_RESUME, jd_keywords, "SDET")

    # Count Java occurrences across all categories
    java_count = 0
    for category, skills in result["skills"].items():
        java_count += sum(1 for s in skills if s.lower() == "java")
    assert java_count == 1


def test_original_not_modified():
    import copy
    original = copy.deepcopy(BASE_RESUME)
    optimize_resume(BASE_RESUME, {"docker", "aws"}, "SDET")
    assert BASE_RESUME == original
