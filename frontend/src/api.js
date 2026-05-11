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

export const compileTypst = async (typstCode) => {
  const blob = new Blob([typstCode], { type: "text/plain" });
  const formData = new FormData();
  formData.append("typst_code", blob, "resume.typ");

  const res = await api.post("/compile-typst", formData, {
    responseType: "blob",
  });
  return res.data;
};