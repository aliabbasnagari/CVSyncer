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

    response = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    )

    print("Response:", response.choices[0].message.content)
    return response.choices[0].message.content


def generate_optimized_typst(resume_text: str, job_description: str):
    prompt = f"""
You are an expert Typst resume writer and ATS optimization specialist.

Task: Create a **professional, clean, one-page Typst resume** that achieves near 100% match with the job description.

Original Resume:
{resume_text}

Job Description:
{job_description}

Requirements:
- Use modern, clean, ATS-friendly Typst markup (single column preferred).
- Incorporate all relevant keywords from the JD naturally.
- Reorder/rephrase experience and skills to prioritize JD requirements.
- Keep it to **one page** (use `#set page(paper: "a4", margin: 1.5cm)` or similar).
- Include sections: Contact, Summary, Experience, Education, Skills, Projects (if relevant).
- Use Typst syntax: `#set text(font: "DejaVu Sans", size: 10pt)`, `= Heading`, `== Subheading`, `- bullet`, `#link(...)`, etc.
- Only rely on built-in Typst features (no external packages / no `#import "@preview/..."`).
- Make the Typst code complete and compilable as-is with the `typst` CLI / Python bindings.

Return ONLY the full Typst code wrapped in ```typst ... ```
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    typst_code = response.choices[0].message.content

    # Extract code if wrapped
    if "```typst" in typst_code:
        typst_code = typst_code.split("```typst")[1].split("```")[0].strip()
    elif "```" in typst_code:
        typst_code = typst_code.split("```")[1].strip()

    return typst_code
