import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeResume, optimizeCV } from "../api";
import UploadBox from "../components/UploadBox";
import ResultCard from "../components/ResultCard";

export default function Dashboard() {
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentFile, setCurrentFile] = useState(null);
  const [currentJobDesc, setCurrentJobDesc] = useState(null);

  const handleAnalyze = async (file, jobText) => {
    const data = await analyzeResume(file, jobText);
    setResult(data);
    setOptimizedCV(null);
    setCurrentFile(file);
    setCurrentJobDesc(jobText);
  };

  const handleOptimize = async () => {
    if (!currentFile || !currentJobDesc) return;

    setIsLoading(true);
    try {
      const data = await optimizeCV(currentFile, currentJobDesc);
      if (data.success) {
        navigate("/editor", {
          state: { typstSource: data.typst, pdfBase64: data.pdf_base64 },
        });
      } else {
        alert("Failed to generate optimized CV. Please try again.");
      }
    } catch (err) {
      console.error("Optimization failed:", err);
      alert("Failed to generate optimized CV. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-10 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">
        AI Resume Screener
      </h1>

      <UploadBox onAnalyze={handleAnalyze} />

      {result && (
        <>
          <ResultCard data={result} onOptimize={handleOptimize} />

          {isLoading && (
            <div className="mt-8 bg-gray-800 p-6 rounded-xl text-center">
              <div className="flex items-center justify-center gap-3 text-gray-300">
                <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Generating your optimized CV…
              </div>
              <p className="text-gray-500 text-sm mt-2">
                This may take up to 30 seconds as we compile your perfect resume
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

