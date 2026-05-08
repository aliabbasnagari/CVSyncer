import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
});

export const analyzeResume = async (resume, jobDescription) => {
  const formData = new FormData();
  formData.append("resume", resume);
  formData.append("job_description", jobDescription);

  const res = await api.post("/analyze", formData);
  return res.data;
};

export const optimizeCV = async (resume, jobDescription) => {
  const formData = new FormData();
  formData.append("resume", resume);
  formData.append("job_description", jobDescription);

  const res = await api.post("/optimize-cv", formData);
  return res.data;
};

export const compileLatex = async (latexCode) => {
  const blob = new Blob([latexCode], { type: "text/plain" });
  const formData = new FormData();
  formData.append("latex_code", blob, "resume.tex");

  const res = await api.post("/compile-latex", formData, {
    responseType: "blob",
  });
  return res.data;
};