import json
import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_API_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL) if BASE_URL else OpenAI(api_key=API_KEY)


def generate_feedback(resume, job, missing):
    prompt = f"""
You are an ATS expert recruiter.

Resume:
{resume}

Job Description:
{job}

Missing Skills:
{missing}

Give:
1. Why score is low/high
2. Improvement suggestions
3. Resume optimization tips
"""

    print("Prompt:", prompt)

    response = client.responses.create(
      model=MODEL,
      input=prompt
    )

    print("Response:", response.output_text)

    # response = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
    # print("Response:", response.choices[0].message.content)
    # return response.choices[0].message.content

    return response.output_text


def generate_optimized_cv_data(
    resume_text: str,
    job_description: str,
    feedback: str | None = None,
) -> dict:
    """Ask the LLM to produce structured CV data conforming to the imprecv schema.

    Optionally takes ATS feedback (e.g. from `generate_feedback`) so the model
    can directly address the weaknesses identified during analysis.

    Returns a Python dict that will be inlined into a Typst template. This avoids
    asking the model to write Typst directly (which it gets wrong in many ways).
    """

    schema_hint = """
Output a single JSON object with this exact shape (omit optional fields if unknown,
but keep top-level keys present and use empty arrays / strings where appropriate):

{
  "personal": {
    "name": "Full Name",
    "email": "name@mail.com",
    "phone": "+1 555 555 5555",      // optional, string
    "url": "https://exp.com",     // optional personal site
    "titles": ["Software Engineer"],  // 1-3 short role titles
    "location": {
      "city": "City",
      "region": "Region/State",
      "country": "Country"
    },
    "profiles": [
      {"network": "LinkedIn", "username": "handle", "url": "https://linkedin.com/in/handle"},
      {"network": "GitHub",   "username": "handle", "url": "https://github.com/handle"}
    ]
  },
  "work": [
    {
      "organization": "Company",
      "url": "https://company.com",   // optional
      "location": "City, Country or Remote",
      "positions": [
        {
          "position": "Role Title",
          "startDate": "YYYY-MM-DD",
          "endDate": "YYYY-MM-DD",   // or the literal string "present"
          "highlights": [
            "Bullet describing impact with metrics, tools, and JD keywords.",
            "Another bullet."
          ]
        }
      ]
    }
  ],
  "education": [
    {
      "institution": "School Name",
      "url": "https://school.edu",   // optional
      "area": "Computer Science",
      "studyType": "Bachelor of Science",
      "startDate": "YYYY-MM-DD",
      "endDate": "YYYY-MM-DD",
      "location": "City, Country",
      "honors": ["GPA 3.4", "Dean's List"],     // optional
      "courses": [],                              // optional
      "highlights": []                            // optional
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "url": "https://example.com",   // optional
      "affiliation": "Personal / University",     // optional
      "startDate": "YYYY-MM-DD",                  // optional
      "endDate": "YYYY-MM-DD",                    // optional
      "highlights": ["What it does, your role, JD-relevant tech."]
    }
  ],
  "skills": [
    {"category": "Frontend", "skills": ["React", "TypeScript"]},
    {"category": "Backend",  "skills": ["Node.js", "Python"]}
  ]
}

Rules:
- Output ONLY the JSON object. No prose, no markdown fences.
- The root MUST be a JSON object (`{...}`), never an array, never the literal `null`.
- NEVER use `null`/`None` for any field. If a value is unknown, omit the key
  OR use an empty string `""` for strings and an empty array `[]` for arrays.
  (Specifically: `personal.titles`, `personal.profiles`, `work`, `education`,
  `projects`, `skills`, and every `highlights`/`courses`/`honors` array must
  either be present as an array or omitted entirely — never `null`.)
- Every object inside an array must itself be a non-null object; do not emit
  `[null]` or arrays containing `null`.
- URLs (`personal.url`, every `profiles[].url`, `work[].url`, `education[].url`,
  `projects[].url`) MUST be either omitted entirely or be a full absolute URL
  including the scheme (e.g. `"https://example.com"`). NEVER use an empty
  string `""` for a URL field, and NEVER include a profile entry whose `url`
  you don't know.
- Use plain ASCII where possible. Dates must be ISO "YYYY-MM-DD" or the string "present".
- Highlights are short strings; you MAY use Typst markup like *bold* or _italic_ inside them.
- Do NOT use the `@` character in highlight strings; spell out "at" instead.
- Tailor wording, ordering, and keyword choices to maximize match with the job description.
""".strip()

    feedback_block = (
        f"\nPrior ATS Feedback (address these weaknesses directly when rewriting):\n\"\"\"\n{feedback}\n\"\"\"\n"
        if feedback
        else ""
    )

    prompt = f"""You are an expert resume writer and ATS optimization specialist.

Task: produce structured CV data (JSON) optimized to match the job description below, 
based on the candidate's original resume. Rephrase, reorder, prioritize content, and generate content to 
maximize keyword overlap with the JD. If prior ATS feedback is provided, explicitly act 
on its suggestions.

Note: If skills and projects related to JD are missing then customize the projects in such a way that 
it can accommodate those skills even if they were not present in the original resume.
Also add random projects with random skills if the original resume is too sparse to ensure the output is rich enough for the template to work with. 

Original Resume:
\"\"\"
{resume_text}
\"\"\"
Job Description:
\"\"\"
{job_description}
\"\"\"
{feedback_block}
\"\"\"
{schema_hint}
"""

    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You output only valid JSON conforming to the user's schema."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )"""

    response = client.responses.create(
      model=MODEL,
      input=prompt
    )

    raw = response.output_text
    raw = (raw or "").strip() or "{}"

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Last-ditch: strip code fences if model ignored response_format
        cleaned = raw.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            data = {}

    # The model may still violate the "root must be an object" rule. Coerce so
    # downstream code (which calls .get) never trips on None or a list.
    if not isinstance(data, dict):
        data = {}

    return data


# NOTE: The legacy `generate_optimized_typst` (which asked the LLM to write
# Typst source directly) has been removed. The model produced too many invalid
# constructs. The pipeline now uses `generate_optimized_cv_data` together with
# the imprecv template in main.py to build a Typst source from structured data.
