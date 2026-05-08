import { useState } from "react";

export default function UploadBox({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [job, setJob] = useState("");

  return (
    <div className="bg-gray-800 p-6 rounded-xl space-y-4">
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="block w-full"
      />

      <textarea
        className="w-full p-3 text-black rounded"
        rows="6"
        placeholder="Paste job description..."
        onChange={(e) => setJob(e.target.value)}
      />

      <button
        className="bg-blue-500 px-4 py-2 rounded"
        onClick={() => onAnalyze(file, job)}
      >
        Analyze
      </button>
    </div>
  );
}