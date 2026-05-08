import re
from typing import List, Set, Dict

# Expanded and better organized skill database
SKILL_DB = {
    # Programming Languages
    "python": ["python", "python3", "py"],
    "java": ["java", "java se", "java ee"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "go": ["go", "golang"],
    "rust": ["rust"],
    "csharp": ["c#", "csharp", ".net"],

    # Frameworks & Libraries
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "react": ["react", "react.js", "reactjs"],
    "nextjs": ["next.js", "nextjs"],
    "node": ["node.js", "nodejs", "node"],
    "express": ["express.js", "expressjs"],
    "spring": ["spring boot", "springboot", "spring framework"],

    # Databases
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],

    # Cloud & DevOps
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "jenkins": ["jenkins"],
    "terraform": ["terraform"],

    # AI/ML
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "pytorch": ["pytorch"],
    "tensorflow": ["tensorflow", "tf"],
    "langchain": ["langchain"],
}

# Flatten the database for easier lookup
SKILL_VARIANTS: Dict[str, List[str]] = {}
CANONICAL_SKILL = {}

for canonical, variants in SKILL_DB.items():
    for variant in variants:
        SKILL_VARIANTS[variant] = canonical
        CANONICAL_SKILL[canonical] = canonical  # self reference


def extract_skills(text: str) -> List[str]:
    if not text:
        return []
    
    text = text.lower()
    found: Set[str] = set()

    # Sort by length (longer phrases first) to avoid partial matches
    for variant in sorted(SKILL_VARIANTS.keys(), key=len, reverse=True):
        # Use word boundaries for most skills, but allow some flexibility
        if re.search(r"(?i)\b" + re.escape(variant) + r"\b", text):
            canonical = SKILL_VARIANTS[variant]
            found.add(canonical)

    return sorted(list(found))


def missing_skills(job_skills: List[str], resume_skills: List[str]) -> List[str]:
    job_set = {s.lower().strip() for s in job_skills}
    resume_set = {s.lower().strip() for s in resume_skills}
    return sorted(list(job_set - resume_set))


# Optional: Add fuzzy matching for even better results
def extract_skills_fuzzy(text: str, threshold: float = 0.85) -> List[str]:
    from rapidfuzz import process, fuzz
    
    text = text.lower()
    found = set()
    
    all_skills = list(SKILL_DB.keys())
    
    for skill in all_skills:
        # Check direct match first
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found.add(skill)
            continue
            
        # Fuzzy match
        result = process.extractOne(skill, [text], scorer=fuzz.partial_ratio)
        if result and result[1] >= threshold * 100:
            found.add(skill)
    
    return sorted(list(found))