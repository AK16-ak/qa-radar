import copy
from typing import Dict, Set


def optimize_resume(base_resume: dict, jd_keywords: Set[str],
                    job_title: str) -> dict:
    """
    Optimize resume for a specific job by:
    1. Injecting ALL JD keywords into the skills section
    2. Rewriting summary to match job title
    3. Reordering skills to put JD-relevant ones first

    Returns a new optimized resume dict (does not modify original).
    """
    resume = copy.deepcopy(base_resume)

    # --- 1. Inject JD keywords into skills ---
    _inject_keywords(resume, jd_keywords)

    # --- 2. Optimize summary for job title ---
    _optimize_summary(resume, job_title, jd_keywords)

    # --- 3. Reorder skills (JD-relevant first) ---
    _reorder_skills(resume, jd_keywords)

    return resume


def _inject_keywords(resume: dict, jd_keywords: Set[str]):
    """Add JD keywords into appropriate skills categories."""
    skills = resume.get("skills", {})

    # Gather all existing skills (lowercased) for dedup
    existing = set()
    for category, skill_list in skills.items():
        for s in skill_list:
            existing.add(s.lower())

    # Categorize and inject missing keywords
    for kw in jd_keywords:
        if kw in existing:
            continue

        category = _categorize_keyword(kw)
        if category not in skills:
            skills[category] = []
        # Title-case the keyword for display
        skills[category].append(_title_case(kw))
        existing.add(kw)

    resume["skills"] = skills


def _optimize_summary(resume: dict, job_title: str, jd_keywords: Set[str]):
    """Rewrite summary to include job title and top JD keywords."""
    years = resume.get("personal", {}).get("total_experience_years", 3)
    top_keywords = sorted(jd_keywords)[:6]
    keyword_str = ", ".join(_title_case(k) for k in top_keywords)

    summary = (
        f"Results-driven {job_title} with {years}+ years of experience in "
        f"test automation, quality assurance, and software testing. "
        f"Proficient in {keyword_str}. "
        f"Proven track record of building robust automation frameworks, "
        f"reducing manual testing effort, and ensuring software reliability "
        f"in Agile environments."
    )
    resume["summary"] = summary


def _reorder_skills(resume: dict, jd_keywords: Set[str]):
    """Put JD-relevant skills at the front of each category list."""
    skills = resume.get("skills", {})
    for category, skill_list in skills.items():
        relevant = [s for s in skill_list if s.lower() in jd_keywords]
        others = [s for s in skill_list if s.lower() not in jd_keywords]
        skills[category] = relevant + others
    resume["skills"] = skills


def _categorize_keyword(keyword: str) -> str:
    """Categorize a keyword into the appropriate skills section."""
    kw = keyword.lower()

    languages = {"java", "python", "javascript", "typescript", "c++", "c#",
                 "ruby", "go", "golang", "kotlin", "scala", "groovy", "php",
                 "swift", "perl"}
    if kw in languages:
        return "programming_languages"

    frameworks = {"selenium", "cypress", "playwright", "appium", "testng",
                  "junit", "pytest", "cucumber", "behave", "karate",
                  "rest assured", "restassured", "webdriverio", "protractor",
                  "robot framework", "katalon", "mocha", "jasmine", "jest",
                  "specflow", "nightwatch"}
    if kw in frameworks:
        return "frameworks"

    databases = {"mysql", "postgresql", "mongodb", "redis", "sql", "oracle",
                 "cassandra", "dynamodb", "elasticsearch"}
    if kw in databases:
        return "databases"

    tools = {"jenkins", "jira", "git", "github", "gitlab", "bitbucket",
             "docker", "kubernetes", "k8s", "aws", "azure", "gcp",
             "maven", "gradle", "allure", "postman", "soapui", "jmeter",
             "gatling", "locust", "k6", "browserstack", "sauce labs",
             "lambdatest", "selenium grid", "charles proxy", "terraform",
             "ansible", "kibana", "grafana", "splunk", "datadog",
             "github actions", "gitlab ci", "circleci", "bamboo",
             "teamcity", "azure devops", "new relic", "kafka", "rabbitmq"}
    if kw in tools:
        return "tools"

    methodologies = {"agile", "scrum", "kanban", "bdd", "tdd", "pom",
                     "page object model", "data-driven testing", "data driven",
                     "shift-left testing", "cross-browser testing",
                     "hybrid framework", "keyword-driven", "microservices"}
    if kw in methodologies:
        return "methodologies"

    # Default: testing types
    return "testing_types"


def _title_case(keyword: str) -> str:
    """Smart title-case for technical terms."""
    # Keep specific casing for known acronyms/tools
    special_cases = {
        "ci/cd": "CI/CD", "ci cd": "CI/CD", "bdd": "BDD", "tdd": "TDD",
        "pom": "POM", "api testing": "API Testing", "rest api": "REST API",
        "api automation": "API Automation", "e2e testing": "E2E Testing",
        "sql": "SQL", "mysql": "MySQL", "postgresql": "PostgreSQL",
        "mongodb": "MongoDB", "aws": "AWS", "gcp": "GCP", "k8s": "K8s",
        "graphql": "GraphQL", "grpc": "gRPC", "soapui": "SoapUI",
        "testng": "TestNG", "junit": "JUnit", "github": "GitHub",
        "gitlab": "GitLab", "bitbucket": "Bitbucket", "jmeter": "JMeter",
        "ui automation": "UI Automation", "rest assured": "Rest Assured",
        "restassured": "Rest Assured", "github actions": "GitHub Actions",
        "gitlab ci": "GitLab CI", "azure devops": "Azure DevOps",
    }
    if keyword.lower() in special_cases:
        return special_cases[keyword.lower()]
    return keyword.title()
