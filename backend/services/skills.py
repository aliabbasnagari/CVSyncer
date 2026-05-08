import re

COMMON_SKILLS = [
    "python", "java", "django", "flask", "react", "node",
    "fastapi", "sql", "postgresql", "docker", "kubernetes",
    "aws", "machine learning", "nlp"
]

def extract_skills(text):
    text = text.lower()
    found = []
    for skill in COMMON_SKILLS:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found.append(skill)
    return list(set(found))


def missing_skills(job_skills, resume_skills):
    return list(set(job_skills) - set(resume_skills))