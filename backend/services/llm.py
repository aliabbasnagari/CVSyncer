import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_API_BASE_URL") 

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
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )

    print("Response:", response.choices[0].message.content)
    return response.choices[0].message.content


def generate_optimized_latex(resume_text: str, job_description: str):
    prompt = f"""
You are an expert LaTeX resume writer and ATS optimization specialist.

Task: Create a **professional, clean, one-page LaTeX resume** that achieves near 100% match with the job description.

Original Resume:
{resume_text}

Job Description:
{job_description}

Requirements:
- Use a modern, clean, ATS-friendly LaTeX template (single column preferred).
- Incorporate all relevant keywords from the JD naturally.
- Reorder/rephrase experience and skills to prioritize JD requirements.
- Keep it to **one page**.
- Use standard packages only: geometry, fontspec or lmodern, hyperref, enumitem, etc.
- Include sections: Contact, Summary, Experience, Education, Skills, Projects (if relevant).
- Make the LaTeX code complete and compilable with xelatex.
- setmainfont TeX Gyre Heros.

Return ONLY the full LaTeX code wrapped in ```latex ... ```
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    latex_code = response.choices[0].message.content

    # Extract code if wrapped
    if "```latex" in latex_code:
        latex_code = latex_code.split("```latex")[1].split("```")[0].strip()
    elif "```" in latex_code:
        latex_code = latex_code.split("```")[1].strip()

    return latex_code
