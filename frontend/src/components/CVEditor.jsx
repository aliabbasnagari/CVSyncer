import { useState, useRef, useEffect } from "react";
import { compileLatex } from "../api";

export default function CVEditor({ latexSource, pdfBase64 }) {
  const [latex, setLatex] = useState(latexSource || "");
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [error, setError] = useState(null);
  const iframeRef = useRef(null);

  // Load initial PDF from base64 if provided
  useEffect(() => {
    if (pdfBase64) {
      try {
        const byteCharacters = atob(pdfBase64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/pdf" });
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);
        if (iframeRef.current) {
          iframeRef.current.src = url;
        }
      } catch (err) {
        console.error("Failed to load initial PDF:", err);
      }
    }
  }, [pdfBase64]);

  // Convert LaTeX to PDF using backend compilation
  const compileToPdf = async (latexCode) => {
    setIsCompiling(true);
    setError(null);

    try {
      const pdfBlob = await compileLatex(latexCode);
      const url = URL.createObjectURL(pdfBlob);
      setPreviewUrl(url);

      if (iframeRef.current) {
        iframeRef.current.src = url;
      }
    } catch (err) {
      setError(err.message || "Compilation failed");
    } finally {
      setIsCompiling(false);
    }
  };

  const handleDownload = async () => {
    if (!previewUrl) {
      await compileToPdf(latex);
    }

    // Trigger download
    const link = document.createElement("a");
    link.href = previewUrl;
    link.download = "optimized_cv.pdf";
    link.click();
  };

  const handleLatexChange = (e) => {
    setLatex(e.target.value);
  };

  const handleCompile = () => {
    compileToPdf(latex);
  };

  return (
    <div className="mt-8 bg-gray-900 border border-gray-700 rounded-3xl overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="px-8 py-6 bg-blue-500/10 border-b border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-white">Optimized CV Editor</h2>
            <p className="text-gray-400 text-sm mt-1">Edit LaTeX and preview your PDF</p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleCompile}
              disabled={isCompiling}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-white px-6 py-2.5 rounded-xl font-medium transition-colors flex items-center gap-2"
            >
              {isCompiling ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Compiling...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Recompile
                </>
              )}
            </button>

            <button
              onClick={handleDownload}
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl font-medium transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download PDF
            </button>
          </div>
        </div>
      </div>

      <div className="p-8">
        {error && (
          <div className="mb-6 bg-red-950/50 border border-red-800 text-red-300 px-4 py-3 rounded-xl">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LaTeX Editor */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              LaTeX Source Code
            </label>
            <textarea
              value={latex}
              onChange={handleLatexChange}
              className="w-full h-96 lg:h-[600px] bg-gray-950 border border-gray-700 rounded-xl p-4 font-mono text-sm text-gray-300 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              spellCheck={false}
            />
            <p className="text-xs text-gray-500 mt-2">
              Edit the LaTeX code above. Click "Preview" to compile and see changes.
            </p>
          </div>

          {/* PDF Preview */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              PDF Preview
            </label>
            <div className="w-full h-96 lg:h-[600px] bg-gray-950 border border-gray-700 rounded-xl overflow-hidden">
              {previewUrl ? (
                <iframe
                  ref={iframeRef}
                  src={previewUrl}
                  className="w-full h-full"
                  title="PDF Preview"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p>Click "Preview" to generate PDF</p>
                  </div>
                </div>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Preview shows the compiled PDF. Download to save locally.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
