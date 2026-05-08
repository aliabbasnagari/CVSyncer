from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from services.parser import extract_text_from_pdf
from services.embedding import get_embedding
from services.matcher import calculate_match
from services.skills import extract_skills, missing_skills
from services.llm import generate_feedback
from services.llm import generate_optimized_latex

import subprocess
import tempfile
import os
from fastapi.responses import FileResponse, JSONResponse

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...), job_description: str = Form(...)
):

    resume_bytes = await resume.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    resume_emb = get_embedding(resume_text)
    job_emb = get_embedding(job_description)

    score = calculate_match(resume_emb, job_emb)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    missing = missing_skills(job_skills, resume_skills)

    feedback = (
        generate_feedback(resume_text, job_description, missing)
        if score < 95
        else "Strong match. Well aligned profile."
    )

    return {
        "match_score": score,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "missing_skills": missing,
        "feedback": feedback,
    }


@app.post("/optimize-cv")
async def optimize_cv(resume: UploadFile = File(...), job_description: str = Form(...)):
    resume_bytes = await resume.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    # Generate LaTeX
    latex_code = generate_optimized_latex(resume_text, job_description)

    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "optimized_cv.tex")
        pdf_path = os.path.join(tmpdir, "optimized_cv.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        # Compile LaTeX to PDF (requires texlive installed on server)
        try:
            subprocess.run(
                [
                    "xelatex",
                    "-interaction=nonstopmode",
                    "-output-directory",
                    tmpdir,
                    tex_path,
                ],
                cwd=tmpdir,
                check=True,
                capture_output=True,
            )

            if os.path.exists(pdf_path):
                # Return both LaTeX source and PDF
                with open(tex_path, "r", encoding="utf-8") as f:
                    latex_source = f.read()

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                import base64

                pdf_base64 = base64.b64encode(pdf_bytes).decode()

                return {
                    "success": True,
                    "latex": latex_source,
                    "pdf_base64": pdf_base64,
                    "message": "100% optimized CV generated successfully",
                }
            else:
                return JSONResponse(
                    status_code=500, content={"error": "PDF compilation failed"}
                )

        except subprocess.CalledProcessError as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "LaTeX compilation error",
                    "details": e.stderr.decode(),
                    "stdout": e.stdout.decode(errors="ignore"),
                    "stderr": e.stderr.decode(errors="ignore"),
                },
            )


@app.post("/compile-latex")
async def compile_latex(latex_code: UploadFile = File(...)):
    """Compile LaTeX code to PDF and return the PDF file."""
    latex_content = await latex_code.read()
    latex_content = latex_content.decode("utf-8")

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_content)

        try:
            subprocess.run(
                [
                    "xelatex",
                    "-interaction=nonstopmode",
                    "-output-directory",
                    tmpdir,
                    tex_path,
                ],
                cwd=tmpdir,
                check=True,
                capture_output=True,
            )

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                from fastapi.responses import Response

                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=resume.pdf"},
                )
            else:
                return JSONResponse(
                    status_code=500, content={"error": "PDF compilation failed"}
                )

        except subprocess.CalledProcessError as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "LaTeX compilation error",
                    "details": e.stderr.decode(),
                    "stdout": e.stdout.decode(errors="ignore"),
                    "stderr": e.stderr.decode(errors="ignore"),
                },
            )
