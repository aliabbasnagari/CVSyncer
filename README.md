# CVSyncer

**Sync Your CV with Your Dream Job**

CVSyncer is an AI-powered resume analysis and optimization tool. Upload your PDF resume alongside a job description to get an ATS match score, skill gap analysis, LLM-generated feedback, and an AI-optimized CV exported as a compiled PDF.

---

## Features

- **Resume Analysis** — Upload a PDF resume and paste a job description to receive a semantic similarity match score (0–100%).
- **Skill Gap Detection** — Automatically extracts skills from both the resume and job description, highlighting what's missing.
- **AI Feedback** — GPT-4o-mini generates actionable improvement suggestions based on the gap analysis.
- **CV Optimization** — GPT-4o rewrites the resume as an ATS-optimized LaTeX document tailored to the job description.
- **LaTeX Editor & PDF Preview** — Edit the generated LaTeX in-browser and compile it to PDF via the backend (`xelatex`).
- **PDF Download** — Download the final optimized CV as a PDF.

---

## Tech Stack

### Backend (FastAPI)
| Component | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| PDF parsing | PyMuPDF (`fitz`) |
| Semantic embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Match scoring | Cosine similarity (`scikit-learn`) |
| Skill extraction | Regex-based keyword matching (`rapidfuzz`) |
| AI feedback & LaTeX generation | OpenAI API (GPT-4o / GPT-4o-mini) |
| LaTeX compilation | `xelatex` (TeX Live) |

### Frontend (React + Vite)
| Component | Technology |
|---|---|
| UI framework | React 19 + Tailwind CSS |
| HTTP client | Axios |
| PDF rendering | `react-pdf` |
| LaTeX syntax highlight | `prism-react-renderer` |
| Markdown rendering | `react-markdown` + `remark-gfm` |

---

## Project Structure

```
CVSyncer/
├── backend/
│   ├── main.py                  # FastAPI app & API routes
│   ├── ai.py                    # Standalone AI utilities
│   ├── requirements.txt
│   ├── Dockerfile
│   └── services/
│       ├── parser.py            # PDF text extraction
│       ├── embedding.py         # Sentence embedding model
│       ├── matcher.py           # Cosine similarity scoring
│       ├── skills.py            # Skill extraction & gap analysis
│       └── llm.py               # OpenAI feedback & LaTeX generation
└── frontend/
    ├── src/
    │   ├── api.js               # Axios API client
    │   ├── App.jsx
    │   ├── pages/
    │   │   └── Dashboard.jsx    # Main dashboard page
    │   └── components/
    │       ├── UploadBox.jsx    # Resume + JD input form
    │       ├── ResultCard.jsx   # Match score & feedback display
    │       └── CVEditor.jsx     # LaTeX editor + PDF preview
    ├── Dockerfile
    └── package.json
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Analyze resume against a job description |
| `POST` | `/optimize-cv` | Generate an optimized LaTeX CV and compile to PDF |
| `POST` | `/compile-latex` | Compile raw LaTeX code to PDF |

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- TeX Live with `xelatex` (for CV compilation)
- OpenAI API key

### Backend

```bash
cd backend
cp .env.example .env
# Add your OPENAI_API_KEY (and optionally OPENAI_API_BASE_URL) to .env

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env   # Set VITE_API_URL if backend is not on localhost:8000

npm install
npm run dev
```

### Docker

Both services include a `Dockerfile`. Run them individually or wire up with Docker Compose.

---

## Environment Variables

### Backend (`.env`)
| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_API_BASE_URL` | (Optional) Custom OpenAI-compatible base URL |
| `OPENAI_MODEL` | (Optional) Model to use (default: `gpt-4o-mini`) |

### Frontend (`.env`)
| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend API URL (default: `http://localhost:8000`) |

