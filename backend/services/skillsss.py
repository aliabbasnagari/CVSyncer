import re
from typing import List, Dict, Set, Tuple

# ====================== SKILL DATABASE ======================
SKILL_DATABASE = {
    # Programming Languages
    "python": ["python", "python3", "py"],
    "java": ["java", "java se", "core java"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "golang": ["golang", "go"],
    "rust": ["rust"],
    "csharp": ["c#", "csharp", ".net", "dotnet"],
    "php": ["php"],
    "ruby": ["ruby"],
    # Frameworks & Backend
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "spring": ["spring boot", "springboot", "spring"],
    "react": ["react", "reactjs", "react.js"],
    "nextjs": ["next.js", "nextjs"],
    "nodejs": ["node.js", "nodejs", "node"],
    "express": ["express.js", "expressjs"],
    # Databases
    "sql": ["sql", "mysql", "postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo db", "mongo"],
    "redis": ["redis"],
    "oracle": ["oracle db"],
    # Cloud & DevOps
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud platform"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "jenkins": ["jenkins"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    # AI / ML / Data
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"],
    "pytorch": ["pytorch"],
    "tensorflow": ["tensorflow", "tf"],
    "langchain": ["langchain"],
    "llm": ["llm", "large language model"],
    "data science": ["data science"],
    # Soft / Other Important Skills
    "agile": ["agile", "scrum"],
    "leadership": ["leadership", "team lead", "tech lead"],
    "communication": ["communication skills", "strong communication"],
}

# Create lookup for fast matching
VARIANTS_TO_CANONICAL = {}
for canonical, variants in SKILL_DATABASE.items():
    for variant in variants:
        VARIANTS_TO_CANONICAL[variant.lower()] = canonical


def extract_skills(text: str) -> Set[str]:
    """Extract skills from any text (JD or Resume)"""
    if not text:
        return set()

    text_lower = text.lower()
    found_skills: Set[str] = set()

    # Sort by length (longest first) to avoid substring issues
    for variant in sorted(VARIANTS_TO_CANONICAL.keys(), key=len, reverse=True):
        # Use word boundary to avoid partial matches like "java" in "javascript"
        pattern = r"\b" + re.escape(variant) + r"\b"
        if re.search(pattern, text_lower):
            canonical_skill = VARIANTS_TO_CANONICAL[variant]
            found_skills.add(canonical_skill)

    return found_skills


def analyze_resume_vs_jd(resume_text: str, jd_text: str) -> Dict:
    """
    Main function to analyze Resume vs Job Description
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    missing_skills = jd_skills - resume_skills
    matched_skills = jd_skills & resume_skills
    extra_skills_in_resume = resume_skills - jd_skills

    match_percentage = (
        round((len(matched_skills) / len(jd_skills) * 100), 1) if jd_skills else 0
    )

    return {
        "jd_required_skills": sorted(jd_skills),
        "candidate_has_skills": sorted(resume_skills),
        "missing_skills": sorted(missing_skills),
        "matched_skills": sorted(matched_skills),
        "extra_skills": sorted(extra_skills_in_resume),
        "match_score": match_percentage,
        "total_required": len(jd_skills),
        "total_matched": len(matched_skills),
    }