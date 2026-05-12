/*
export default function ResultCard({ data }) {
  return (
    <div className="mt-6 bg-gray-800 p-6 rounded-xl space-y-3">
      <h2 className="text-xl font-bold">
        Match Score: {data.match_score}%
      </h2>

      <div>
        <h3 className="font-semibold">Missing Skills</h3>
        <div className="flex flex-wrap gap-2">
          {data.missing_skills.map((s, i) => (
            <span
              key={i}
              className="bg-red-600 px-2 py-1 rounded"
            >
              {s}
            </span>
          ))}
        </div>
      </div>

      <div>
        <h3 className="font-semibold">Feedback</h3>
        <p className="text-gray-300">{data.feedback}</p>
      </div>
    </div>
  );
}
*/

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ResultCard({ data, onOptimize, isOptimizing = false }) {
  const { match_score, missing_skills, feedback } = data;

  const getScoreColor = (score) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-amber-400";
    return "text-red-400";
  };

  const getScoreBg = (score) => {
    if (score >= 80) return "bg-emerald-500/10 border-emerald-500/30";
    if (score >= 60) return "bg-amber-500/10 border-amber-500/30";
    return "bg-red-500/10 border-red-500/30";
  };

  return (
    <div className="mt-8 bg-gray-900 border border-gray-700 rounded-3xl overflow-hidden shadow-2xl">
      {/* Header */}
      <div className={`px-8 py-7 ${getScoreBg(match_score)} border-b border-gray-700`}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-white">Resume Match Analysis</h2>
            <p className="text-gray-400 text-sm mt-1">AI-powered feedback</p>
          </div>

          <div className="text-center sm:text-right">
            <div className="text-sm uppercase tracking-widest text-gray-500 font-medium">Match Score</div>
            <div className={`text-6xl font-bold tracking-tighter ${getScoreColor(match_score)}`}>
              {match_score}
              <span className="text-3xl font-normal">%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8 space-y-10">
        {/* Missing Skills */}
        {missing_skills && missing_skills.length > 0 && (
          <div>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-9 h-9 rounded-2xl bg-red-500/10 flex items-center justify-center text-red-400 text-xl">
                ⚠️
              </div>
              <h3 className="text-xl font-semibold text-white">Missing / Weak Skills</h3>
            </div>

            <div className="flex flex-wrap gap-3">
              {missing_skills.map((skill, i) => (
                <span
                  key={i}
                  className="bg-red-950 hover:bg-red-900 transition-colors border border-red-800 text-red-300 px-5 py-2.5 rounded-2xl text-sm font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Feedback with Markdown Support */}
        <div>
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400 text-xl">
              💡
            </div>
            <h3 className="text-xl font-semibold text-white">Detailed Feedback</h3>
          </div>

          <div className="prose prose-invert prose-gray max-w-none bg-gray-800/70 border border-gray-700 rounded-2xl p-7 leading-relaxed">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({node, ...props}) => <h1 className="text-2xl font-bold mt-6 mb-3 text-white" {...props} />,
                h2: ({node, ...props}) => <h2 className="text-xl font-semibold mt-5 mb-3 text-white" {...props} />,
                h3: ({node, ...props}) => <h3 className="text-lg font-medium mt-4 mb-2 text-gray-100" {...props} />,
                p: ({node, ...props}) => <p className="mb-4 text-gray-300 leading-relaxed" {...props} />,
                ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-4 space-y-2 text-gray-300" {...props} />,
                ol: ({node, ...props}) => <ol className="list-decimal pl-6 mb-4 space-y-2 text-gray-300" {...props} />,
                li: ({node, ...props}) => <li className="mb-1" {...props} />,
                strong: ({node, ...props}) => <strong className="font-semibold text-white" {...props} />,
                code: ({node, inline, ...props}) => 
                  inline ? (
                    <code className="bg-gray-900 px-1.5 py-0.5 rounded text-sm font-mono text-amber-300" {...props} />
                  ) : (
                    <code className="block bg-gray-950 p-4 rounded-xl overflow-x-auto text-sm font-mono text-gray-300" {...props} />
                  ),
                blockquote: ({node, ...props}) => (
                  <blockquote className="border-l-4 border-gray-600 pl-4 italic text-gray-400 my-4" {...props} />
                ),
              }}
            >
              {feedback || "No feedback available."}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {/* Footer with Optimize Button */}
      <div className="bg-gray-950 px-8 py-5 border-t border-gray-700">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="text-xs text-gray-500">
            <p>✦ Powered by AI Resume Analyzer</p>
            <p className="mt-1">Tip: Focus on the highlighted skills to significantly improve your match score</p>
          </div>

          {match_score < 100 && onOptimize && (
            <button
              onClick={onOptimize}
              disabled={isOptimizing}
              aria-busy={isOptimizing}
              className="bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:from-blue-600 disabled:hover:to-emerald-600 text-white px-6 py-3 rounded-xl font-medium transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              {isOptimizing ? (
                <>
                  <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating…
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Generate Optimized CV
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}