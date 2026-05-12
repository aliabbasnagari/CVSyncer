import { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { compileTypst } from "../api";

export default function CVEditorPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { typstSource, pdfBase64 } = location.state || {};

  const [typstCode, setTypstCode] = useState(typstSource || "");
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [error, setError] = useState(null);
  const [splitPos, setSplitPos] = useState(50); // percentage
  const [lineCount, setLineCount] = useState(1);

  const iframeRef = useRef(null);
  const textareaRef = useRef(null);
  const lineNumbersRef = useRef(null);
  const isDragging = useRef(false);
  const containerRef = useRef(null);

  // Load initial PDF from base64
  useEffect(() => {
    if (pdfBase64) {
      try {
        const byteCharacters = atob(pdfBase64);
        const byteArray = new Uint8Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteArray[i] = byteCharacters.charCodeAt(i);
        }
        const blob = new Blob([byteArray], { type: "application/pdf" });
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);
      } catch (err) {
        console.error("Failed to load initial PDF:", err);
      }
    }
  }, [pdfBase64]);

  // Update line count when source changes
  useEffect(() => {
    setLineCount(typstCode.split("\n").length);
  }, [typstCode]);

  // Sync line numbers scroll with textarea
  const syncScroll = () => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  const compileToPdf = async (source) => {
    setIsCompiling(true);
    setError(null);
    try {
      const pdfBlob = await compileTypst(source);
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

  const handleDownload = () => {
    if (!previewUrl) return;
    const link = document.createElement("a");
    link.href = previewUrl;
    link.download = "optimized_cv.pdf";
    link.click();
  };

  // Draggable divider
  const handleDividerMouseDown = (e) => {
    isDragging.current = true;
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const newPos = ((e.clientX - rect.left) / rect.width) * 100;
      setSplitPos(Math.min(Math.max(newPos, 20), 80));
    };
    const handleMouseUp = () => {
      isDragging.current = false;
    };
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  return (
    <div className="h-screen flex flex-col bg-gray-950 text-white overflow-hidden select-none">
      {/* Top Bar */}
      <div className="flex items-center gap-3 px-5 py-3 bg-gray-900 border-b border-gray-800 shrink-0">
        {/* Back */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-800"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>

        <div className="w-px h-5 bg-gray-700" />

        {/* Title */}
        <div className="flex items-center gap-2 flex-1">
          <div className="w-2 h-2 rounded-full bg-blue-500" />
          <h2 className="text-sm font-semibold text-white">CV Typst Editor</h2>
          <span className="text-xs text-gray-500 ml-2">{lineCount} lines</span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => compileToPdf(typstCode)}
            disabled={isCompiling}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm px-4 py-1.5 rounded-lg font-medium transition-colors"
          >
            {isCompiling ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Compiling…
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Compile
              </>
            )}
          </button>

          <button
            onClick={handleDownload}
            disabled={!previewUrl}
            className="flex items-center gap-2 bg-emerald-700 hover:bg-emerald-600 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm px-4 py-1.5 rounded-lg font-medium transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="shrink-0 flex items-center gap-3 bg-red-950/60 border-b border-red-800 px-5 py-2.5 text-sm text-red-300">
          <svg className="w-4 h-4 shrink-0 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-medium">Compile Error:</span> {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-200">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Split Panel */}
      <div ref={containerRef} className="flex flex-1 overflow-hidden">
        {/* Left: Typst Editor */}
        <div
          style={{ width: `${splitPos}%` }}
          className="flex flex-col overflow-hidden"
        >
          {/* Panel Header */}
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-900/80 border-b border-gray-800 shrink-0">
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Typst Source</span>
            <div className="ml-auto flex gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-gray-700" />
              <div className="w-2.5 h-2.5 rounded-full bg-gray-700" />
              <div className="w-2.5 h-2.5 rounded-full bg-gray-700" />
            </div>
          </div>

          {/* Editor Area */}
          <div className="flex flex-1 overflow-hidden bg-gray-950">
            {/* Line Numbers */}
            <div
              ref={lineNumbersRef}
              className="shrink-0 overflow-hidden text-right select-none bg-gray-900/50 border-r border-gray-800"
              style={{ minWidth: "3.5rem", paddingTop: "1rem", paddingBottom: "1rem", paddingRight: "0.75rem", paddingLeft: "0.5rem" }}
            >
              {Array.from({ length: lineCount }, (_, i) => (
                <div
                  key={i}
                  className="text-xs text-gray-600 font-mono"
                  style={{ lineHeight: "1.5rem", height: "1.5rem" }}
                >
                  {i + 1}
                </div>
              ))}
            </div>

            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={typstCode}
              onChange={(e) => setTypstCode(e.target.value)}
              onScroll={syncScroll}
              className="flex-1 bg-transparent text-gray-200 resize-none outline-none font-mono text-sm overflow-auto"
              style={{
                lineHeight: "1.5rem",
                padding: "1rem 1rem 1rem 0.75rem",
                tabSize: 2,
              }}
              spellCheck={false}
              autoCorrect="off"
              autoCapitalize="off"
            />
          </div>

          {/* Status bar */}
          <div className="shrink-0 flex items-center gap-4 px-4 py-1.5 bg-gray-900/80 border-t border-gray-800">
            <span className="text-xs text-gray-600">Typst</span>
            <span className="text-xs text-gray-600">{typstCode.length} chars</span>
            <span className="text-xs text-gray-600 ml-auto">Drag divider to resize</span>
          </div>
        </div>

        {/* Draggable Divider */}
        <div
          onMouseDown={handleDividerMouseDown}
          className="w-1 bg-gray-800 hover:bg-blue-500/60 cursor-col-resize transition-colors shrink-0 active:bg-blue-500"
          title="Drag to resize"
        />

        {/* Right: PDF Preview */}
        <div
          style={{ width: `${100 - splitPos - 0.2}%` }}
          className="flex flex-col overflow-hidden"
        >
          {/* Panel Header */}
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-900/80 border-b border-gray-800 shrink-0">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">PDF Preview</span>
            {previewUrl && (
              <span className="ml-auto text-xs text-emerald-500">● Live</span>
            )}
          </div>

          {/* PDF or placeholder */}
          <div className="flex-1 overflow-hidden bg-gray-800/40">
            {previewUrl ? (
              <iframe
                ref={iframeRef}
                src={previewUrl}
                className="w-full h-full border-0"
                title="PDF Preview"
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center gap-4 text-gray-600">
                <svg className="w-20 h-20 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-500">No preview yet</p>
                  <p className="text-xs text-gray-600 mt-1">Click <span className="text-blue-400">Compile</span> to generate the PDF</p>
                </div>
                <button
                  onClick={() => compileToPdf(typstCode)}
                  disabled={isCompiling || !typstCode.trim()}
                  className="flex items-center gap-2 bg-blue-600/20 hover:bg-blue-600/40 border border-blue-600/40 text-blue-400 text-sm px-5 py-2 rounded-lg transition-colors disabled:opacity-40"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Compile Now
                </button>
              </div>
            )}
          </div>

          {/* Preview status bar */}
          <div className="shrink-0 flex items-center gap-4 px-4 py-1.5 bg-gray-900/80 border-t border-gray-800">
            <span className="text-xs text-gray-600">
              {previewUrl ? "PDF ready" : "Awaiting compilation"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
