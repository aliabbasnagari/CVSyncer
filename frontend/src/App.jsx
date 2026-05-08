import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CVEditorPage from "./pages/CVEditorPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={
          <div className="min-h-screen bg-gray-900 text-white">
            <Dashboard />
          </div>
        } />
        <Route path="/editor" element={<CVEditorPage />} />
      </Routes>
    </BrowserRouter>
  );
}
