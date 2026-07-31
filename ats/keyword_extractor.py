import re
from typing import Set

# Master keyword dictionary — common SDET/QA/Automation keywords to look for in JDs
KEYWORD_BANK = {
    # Programming languages
    "java", "python", "javascript", "typescript", "c++", "c#", "ruby", "go", "golang",
    "kotlin", "scala", "groovy", "php", "swift", "perl",
    # Automation frameworks
    "selenium", "cypress", "playwright", "appium", "testng", "junit", "pytest",
    "robot framework", "cucumber", "behave", "specflow", "karate", "rest assured",
    "restassured", "webdriverio", "protractor", "katalon", "tosca", "uft",
    "watir", "capybara", "nightwatch", "mocha", "jasmine", "jest",
    # CI/CD & DevOps
    "jenkins", "ci/cd", "ci cd", "github actions", "gitlab ci", "circleci",
    "travis ci", "azure devops", "bamboo", "teamcity", "docker", "kubernetes",
    "k8s", "aws", "azure", "gcp", "terraform", "ansible",
    # API & Performance
    "api testing", "rest api", "graphql", "postman", "soapui", "soap",
    "jmeter", "gatling", "locust", "k6", "loadrunner", "performance testing",
    "load testing", "stress testing",
    # Tools
    "jira", "git", "github", "gitlab", "bitbucket", "maven", "gradle",
    "allure", "extent reports", "testlink", "zephyr", "xray", "browserstack",
    "sauce labs", "lambdatest", "selenium grid", "charles proxy", "fiddler",
    "kibana", "grafana", "splunk", "datadog", "new relic",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "sql", "oracle", "cassandra",
    "dynamodb", "elasticsearch",
    # Methodologies & Concepts
    "agile", "scrum", "kanban", "bdd", "tdd", "pom", "page object model",
    "data-driven testing", "data driven", "keyword-driven", "hybrid framework",
    "cross-browser testing", "mobile testing", "regression testing",
    "functional testing", "integration testing", "smoke testing",
    "sanity testing", "end-to-end testing", "e2e testing", "api automation",
    "ui automation", "test strategy", "test plan", "test cases",
    "defect management", "bug tracking", "shift-left testing",
    # Messaging & Microservices
    "kafka", "rabbitmq", "microservices", "rest", "grpc", "soap",
}


def extract_keywords(jd_text: str) -> Set[str]:
    """
    Extract relevant technical keywords from a job description.
    Returns a set of matched keywords (lowercased).
    """
    if not jd_text:
        return set()

    text = jd_text.lower()
    found = set()

    for keyword in KEYWORD_BANK:
        # Use word boundary matching for short keywords to avoid false positives
        if len(keyword) <= 3:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, text):
                found.add(keyword)
        else:
            if keyword in text:
                found.add(keyword)

    return found


def get_resume_keywords(resume_data: dict) -> Set[str]:
    """
    Extract all keywords present in the resume data.
    Collects from skills, experience bullets, projects, and summary.
    """
    text_parts = []

    # Summary
    if resume_data.get("summary"):
        text_parts.append(resume_data["summary"])

    # Skills sections
    skills = resume_data.get("skills", {})
    for category, skill_list in skills.items():
        if isinstance(skill_list, list):
            text_parts.extend(skill_list)

    # Experience bullets
    for exp in resume_data.get("experience", []):
        for bullet in exp.get("bullets", []):
            text_parts.append(bullet)

    # Project bullets
    for proj in resume_data.get("projects", []):
        for bullet in proj.get("bullets", []):
            text_parts.append(bullet)

    full_text = " ".join(text_parts).lower()
    found = set()

    for keyword in KEYWORD_BANK:
        if len(keyword) <= 3:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, full_text):
                found.add(keyword)
        else:
            if keyword in full_text:
                found.add(keyword)

    return found
