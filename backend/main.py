import base64
import os
import tempfile

import typst
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from services.embedding import get_embedding
from services.llm import generate_feedback, generate_optimized_typst
from services.matcher import calculate_match
from services.parser import extract_text_from_pdf
from services.skills import extract_skills, missing_skills

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _compile_typst_to_pdf(typst_source: str) -> bytes:
    """Compile a Typst source string to PDF bytes using the typst Python bindings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        typ_path = os.path.join(tmpdir, "doc.typ")
        with open(typ_path, "w", encoding="utf-8") as f:
            f.write(typst_source)
        # typst.compile returns bytes when no output path is given
        return typst.compile(typ_path)


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

    # Generate Typst source via LLM
    typst_code = generate_optimized_typst(resume_text, job_description)

    try:
        pdf_bytes = _compile_typst_to_pdf(typst_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Typst compilation error",
                "details": str(e),
            },
        )

    pdf_base64 = base64.b64encode(pdf_bytes).decode()

    return {
        "success": True,
        "typst": typst_code,
        "pdf_base64": pdf_base64,
        "message": "100% optimized CV generated successfully",
    }


@app.post("/compile-typst")
async def compile_typst(typst_code: UploadFile = File(...)):
    """Compile Typst source to PDF and return the PDF file."""
    typst_source = (await typst_code.read()).decode("utf-8")

    try:
        pdf_bytes = _compile_typst_to_pdf(typst_source)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Typst compilation error",
                "details": str(e),
            },
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"},
    )
