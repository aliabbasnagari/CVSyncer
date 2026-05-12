import base64
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import typst
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from services.embedding import get_embedding
from services.llm import (
    generate_feedback,
    generate_optimized_cv_data,
)
from services.matcher import calculate_match
from services.parser import extract_text_from_pdf
from services.skills import analyze_resume_vs_jd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# imprecv template integration
# ---------------------------------------------------------------------------

IMPRECV_DIR = Path(__file__).parent / "imprecv"
IMPRECV_FILES = ("cv.typ", "utils.typ")  # files we copy next to user source


def _typst_value(v: Any) -> str:
    """Serialize a Python value into a Typst literal expression.

    Supports None, bool, int, float, str, list, dict. Strings are quoted with
    backslash and double-quote escaped. Dict keys must be valid Typst
    identifiers (we control them in our schema, so this is safe).
    """
    if v is None:
        return "none"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        s = v.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{s}"'
    if isinstance(v, list):
        if not v:
            return "()"
        inner = ", ".join(_typst_value(x) for x in v)
        # Trailing comma for single-element to force array, not group.
        if len(v) == 1:
            return f"({inner},)"
        return f"({inner})"
    if isinstance(v, dict):
        if not v:
            return "(:)"
        parts = []
        for k, val in v.items():
            key = str(k)
            if not (key.replace("_", "").isalnum() and not key[0].isdigit()):
                key = f'"{key}"'
            parts.append(f"{key}: {_typst_value(val)}")
        return "(" + ", ".join(parts) + ")"
    raise TypeError(f"Cannot serialize {type(v).__name__} to Typst")


_TEMPLATE_PREAMBLE = '''#import "cv.typ": *

#let uservars = (
    headingfont: "Libertinus Serif",
    bodyfont: "Libertinus Serif",
    fontsize: 10pt,
    linespacing: 6pt,
    sectionspacing: 0pt,
    showAddress: true,
    showNumber: true,
    showTitle: true,
    headingsmallcaps: false,
    sendnote: false,
)

#let customrules(doc) = {
    set page(
        paper: "a4",
        numbering: "1 / 1",
        number-align: center,
        margin: 1.25cm,
    )
    doc
}

#let cvinit(doc) = {
    doc = setrules(uservars, doc)
    doc = showrules(uservars, doc)
    doc = customrules(doc)
    doc
}

#show: doc => cvinit(doc)
'''

_TEMPLATE_BODY = '''
#cvheading(cvdata, uservars)
#cvwork(cvdata)
#cveducation(cvdata)
#cvprojects(cvdata)
#cvskills(cvdata)
#endnote(uservars)
'''


def _clean_url(value: Any) -> Any:
    """Return None for empty/blank/malformed URLs; otherwise the value as-is.

    imprecv's templates do `something.url != none` then call `link(url)` (and
    sometimes `url.split("//").at(1)`), so empty strings either render broken
    links or crash the compile. Normalize them to `None` instead.
    """
    if not isinstance(value, str):
        return value if value is not None else None
    v = value.strip()
    return v or None


def _clean_date(value: Any) -> str:
    """Normalize a date string to either an ISO YYYY-MM-DD or "present".

    imprecv's `strpdate` blindly slices the string, so empty/malformed values
    crash the compile. We coerce anything we can't recognize into "present".
    """
    if not isinstance(value, str):
        return "present"
    v = value.strip()
    if not v:
        return "present"
    if v.lower() == "present":
        return "present"
    # Accept YYYY, YYYY-MM, YYYY-MM-DD; pad to YYYY-MM-DD if needed.
    parts = v.split("-")
    if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
        year = parts[0]
        month = parts[1] if len(parts) > 1 and parts[1].isdigit() else "01"
        day = parts[2] if len(parts) > 2 and parts[2].isdigit() else "01"
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return "present"


def _normalize_cv_data(data: dict) -> dict:
    """Fill in keys that imprecv's cv.typ accesses unconditionally.

    The template eagerly reads several fields (even where it also checks
    membership with `in`), so absent keys cause `dictionary does not contain
    key X` errors. We fill missing fields with empty/None defaults.
    """
    data = dict(data or {})

    # personal
    personal = dict(data.get("personal") or {})
    personal.setdefault("name", "")
    personal.setdefault("email", "")
    personal.setdefault("phone", None)
    personal.setdefault("url", None)
    personal.setdefault("titles", None)
    personal.setdefault("location", None)

    # imprecv eagerly calls `personal.url.split("//").at(1)` whenever url is
    # not `none`, so an empty string would crash. Treat empty/whitespace as
    # absent.
    if isinstance(personal.get("url"), str) and not personal["url"].strip():
        personal["url"] = None

    # Same problem for each profile: it does `profile.url.split("//").at(1)`
    # unconditionally. Drop profiles without a usable url, and drop the whole
    # entry if it can't render at all.
    cleaned_profiles = []
    for prof in personal.get("profiles") or []:
        if not isinstance(prof, dict):
            continue
        url = prof.get("url")
        if not isinstance(url, str) or "//" not in url:
            # Skip profiles whose url is missing/empty/malformed — imprecv would crash.
            continue
        cleaned_profiles.append({
            "network": prof.get("network") or "",
            "username": prof.get("username") or "",
            "url": url,
        })
    personal["profiles"] = cleaned_profiles
    data["personal"] = personal

    # work
    work = []
    for w in data.get("work") or []:
        if not isinstance(w, dict):
            continue
        w = dict(w)
        w.setdefault("organization", "")
        w.setdefault("location", "")
        w["url"] = _clean_url(w.get("url"))
        positions = []
        for p in w.get("positions") or []:
            if not isinstance(p, dict):
                continue
            p = dict(p)
            p.setdefault("position", "")
            p["startDate"] = _clean_date(p.get("startDate"))
            p["endDate"] = _clean_date(p.get("endDate"))
            p.setdefault("highlights", [])
            positions.append(p)
        w["positions"] = positions
        work.append(w)
    data["work"] = work or None

    # education
    education = []
    for e in data.get("education") or []:
        if not isinstance(e, dict):
            continue
        e = dict(e)
        e.setdefault("institution", "")
        e.setdefault("location", "")
        e.setdefault("studyType", "")
        e.setdefault("area", None)
        e["startDate"] = _clean_date(e.get("startDate"))
        e["endDate"] = _clean_date(e.get("endDate"))
        e["url"] = _clean_url(e.get("url"))
        education.append(e)
    data["education"] = education or None

    # projects
    projects = []
    for p in data.get("projects") or []:
        if not isinstance(p, dict):
            continue
        p = dict(p)
        p.setdefault("name", "")
        p.setdefault("affiliation", "")
        p["startDate"] = _clean_date(p.get("startDate"))
        p["endDate"] = _clean_date(p.get("endDate"))
        p.setdefault("highlights", [])
        p["url"] = _clean_url(p.get("url"))
        projects.append(p)
    data["projects"] = projects or None

    # skills (list of {category, skills})
    skills = []
    for s in data.get("skills") or []:
        if isinstance(s, str):
            # LLM sometimes returns a flat list of skill names — wrap it.
            skills.append({"category": "", "skills": [s]})
            continue
        if not isinstance(s, dict):
            continue
        s = dict(s)
        s.setdefault("category", "")
        s.setdefault("skills", [])
        skills.append(s)
    data["skills"] = skills or None

    # Top-level optional sections imprecv may touch
    for key in ("affiliations", "awards", "certificates", "publications", "languages", "interests", "references"):
        data.setdefault(key, None)

    return data


def _build_main_typ(cv_data: dict) -> str:
    """Build a self-contained Typst source that imports cv.typ and inlines data."""
    cv_data = _normalize_cv_data(cv_data)
    return (
        _TEMPLATE_PREAMBLE
        + f"\n#let cvdata = {_typst_value(cv_data)}\n"
        + _TEMPLATE_BODY
    )


def _compile_typst_to_pdf(typst_source: str) -> bytes:
    """Compile a Typst source string to PDF bytes.

    The compile dir is seeded with the local imprecv files so that
    `#import "cv.typ"` (and its `#import "utils.typ"`) resolve.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for name in IMPRECV_FILES:
            src = IMPRECV_DIR / name
            if src.exists():
                shutil.copy(src, tmp / name)
        typ_path = tmp / "main.typ"
        typ_path.write_text(typst_source, encoding="utf-8")
        return typst.compile(str(typ_path))



@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...), job_description: str = Form(...)
):
    resume_bytes = await resume.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    resume_emb = get_embedding(resume_text)
    job_emb = get_embedding(job_description)

    score = calculate_match(resume_emb, job_emb)

    skill_report = analyze_resume_vs_jd(resume_text, job_description)
    missing = skill_report["missing_skills"]

    feedback = (
        generate_feedback(resume_text, job_description, missing)
        if score < 95
        else "Strong match. Well aligned profile."
    )

    return {
        "match_score": score,
        "resume_skills": skill_report["candidate_has_skills"],
        "job_skills": skill_report["jd_required_skills"],
        "matched_skills": skill_report["matched_skills"],
        "missing_skills": missing,
        "extra_skills": skill_report["extra_skills"],
        "skill_match_score": skill_report["match_score"],
        "total_required": skill_report["total_required"],
        "total_matched": skill_report["total_matched"],
        "feedback": feedback,
    }


@app.post("/optimize-cv")
async def optimize_cv(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    feedback: str | None = Form(None),
):
    resume_bytes = await resume.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    # 1. Ask LLM for structured CV data (JSON), not Typst code.
    try:
        cv_data = generate_optimized_cv_data(
            resume_text, job_description, feedback=feedback
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "LLM error", "details": str(e)},
        )

    # 2. Build a self-contained Typst source using the imprecv template.
    typst_code = _build_main_typ(cv_data)

    # 3. Compile to PDF.
    try:
        pdf_bytes = _compile_typst_to_pdf(typst_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Typst compilation error",
                "details": str(e),
                "typst": typst_code,
            },
        )

    pdf_base64 = base64.b64encode(pdf_bytes).decode()

    return {
        "success": True,
        "typst": typst_code,
        "pdf_base64": pdf_base64,
        "message": "Optimized CV generated successfully",
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
