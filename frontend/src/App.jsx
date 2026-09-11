import { useState, useEffect } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import api from "./api";
import UploadForm from "./UploadForm";
import PaperDetail from "./PaperDetail";
import ComparisonView from "./ComparisonView";

function PapersList() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const navigate = useNavigate();

  const fetchPapers = () => {
    setLoading(true);
    api.get("/papers")
      .then((response) => {
        setPapers(response.data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to load papers. Is the backend running?");
        setLoading(false);
        console.error(err);
      });
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((pid) => pid !== id);
      }
      if (prev.length >= 5) {
        alert("You can compare a maximum of 5 papers at once.");
        return prev;
      }
      return [...prev, id];
    });
  };

  const handleCompare = () => {
    if (selectedIds.length < 2) {
      alert("Select at least 2 papers to compare.");
      return;
    }
    navigate(`/compare?ids=${selectedIds.join(",")}`);
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "800px", margin: "0 auto" }}>
      <h1>ResearchOS</h1>

      <UploadForm onUploadComplete={fetchPapers} />

      <h2>Uploaded Papers</h2>
      {loading && <p>Loading papers...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && papers.length === 0 && <p>No papers uploaded yet.</p>}

      {!loading && !error && papers.length > 0 && (
        <>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {papers.map((paper) => (
              <li key={paper.id} style={{ marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                {paper.status === "analyzed" && (
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(paper.id)}
                    onChange={() => toggleSelect(paper.id)}
                  />
                )}
                <Link to={`/papers/${paper.id}`}>
                  <strong>{paper.title || paper.filename}</strong>
                </Link>
                <span style={{ color: "#888" }}>— {paper.status}</span>
              </li>
            ))}
          </ul>

          {selectedIds.length > 0 && (
            <div style={{ marginTop: "1rem", padding: "1rem", background: "#eef", borderRadius: "8px" }}>
              <p>{selectedIds.length} paper(s) selected.</p>
              <button onClick={handleCompare} disabled={selectedIds.length < 2}>
                Compare Selected Papers
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<PapersList />} />
      <Route path="/papers/:id" element={<PaperDetail />} />
      <Route path="/compare" element={<ComparisonView />} />
    </Routes>
  );
}

export default App;