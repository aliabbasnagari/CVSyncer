import { useState, useRef } from "react";

export default function UploadBox({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [job, setJob] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };

  const handleSubmit = async () => {
    if (!file || !job.trim()) return;
    setIsLoading(true);
    try {
      await onAnalyze(file, job);
    } finally {
      setIsLoading(false);
    }
  };

  const canSubmit = file && job.trim() && !isLoading;

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-3xl overflow-hidden shadow-2xl">
      <div className="px-8 py-6 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">Upload & Analyze</h2>
        <p className="text-sm text-gray-500 mt-0.5">Upload your resume and paste the job description below</p>
      </div>

      <div className="p-8 space-y-6">
        {/* Drop Zone */}
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`relative flex flex-col items-center justify-center gap-3 border-2 border-dashed rounded-2xl py-10 cursor-pointer transition-all
            ${isDragging
              ? "border-blue-500 bg-blue-500/10"
              : file
                ? "border-emerald-600/60 bg-emerald-950/20"
                : "border-gray-700 bg-gray-800/40 hover:border-gray-500 hover:bg-gray-800/70"
            }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => setFile(e.target.files[0])}
            className="hidden"
          />

          {file ? (
            <>
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/15 flex items-center justify-center">
                <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-emerald-400">{file.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{(file.size / 1024).toFixed(1)} KB — click to replace</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-12 h-12 rounded-2xl bg-gray-700/60 flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-300">
                  Drop your resume here, or <span className="text-blue-400">browse</span>
                </p>
                <p className="text-xs text-gray-600 mt-0.5">PDF, DOC, DOCX supported</p>
              </div>
            </>
          )}
        </div>

        {/* Job Description */}
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Job Description</label>
          <textarea
            value={job}
            onChange={(e) => setJob(e.target.value)}
            rows={7}
            placeholder="Paste the full job description here…"
            className="w-full bg-gray-800/60 border border-gray-700 focus:border-blue-500/60 focus:ring-2 focus:ring-blue-500/20 text-gray-200 placeholder-gray-600 rounded-2xl px-5 py-4 text-sm resize-none outline-none transition-all"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="w-full flex items-center justify-center gap-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed text-white font-semibold py-3.5 rounded-2xl transition-colors text-sm"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Analyzing…
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              Analyze Resume
            </>
          )}
        </button>
      </div>
    </div>
  );
}
