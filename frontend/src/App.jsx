import { useState, useEffect } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import api from "./api";
import UploadForm from "./UploadForm";
import PaperDetail from "./PaperDetail";
import ComparisonView from "./ComparisonView";

function TopBar() {
  return (
    <div className="topbar">
      <Link to="/" style={{ textDecoration: "none" }}>
        <span className="wordmark">ResearchOS</span>
      </Link>
    </div>
  );
}

function PapersList() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const navigate = useNavigate();

  const fetchPapers = () => {
    setLoading(true);
    api.get("/papers")
      .then((res) => { setPapers(res.data); setLoading(false); })
      .catch((err) => {
        setError("Couldn't reach the server. Make sure the backend is running.");
        setLoading(false);
        console.error(err);
      });
  };

  useEffect(() => { fetchPapers(); }, []);

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((pid) => pid !== id);
      if (prev.length >= 5) { alert("You can compare up to 5 papers at once."); return prev; }
      return [...prev, id];
    });
  };

  const handleCompare = () => {
    if (selectedIds.length < 2) { alert("Select at least 2 papers to compare."); return; }
    navigate(`/compare?ids=${selectedIds.join(",")}`);
  };

  return (
    <div className="page">
      <div style={{ marginBottom: "2.5rem" }}>
        <h1>Your library</h1>
        <p style={{ color: "var(--muted)", marginTop: "0.4rem" }}>
          Upload papers, extract structured findings, compare across your reading list.
        </p>
      </div>

      <UploadForm onUploadComplete={fetchPapers} />

      <div style={{ marginTop: "2.5rem" }}>
        <h2>Papers</h2>

        {loading && <p style={{ color: "var(--muted)" }}>Loading…</p>}
        {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
        {!loading && !error && papers.length === 0 && (
          <p style={{ color: "var(--muted)" }}>Nothing here yet — upload a paper above to begin.</p>
        )}

        {!loading && !error && papers.length > 0 && (
          <div style={{ borderTop: "1px solid var(--line)" }}>
            {papers.map((paper, i) => (
              <div
                key={paper.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  padding: "0.9rem 0",
                  borderBottom: "1px solid var(--line)",
                }}
              >
                <span style={{ color: "var(--muted)", fontSize: "0.85rem", width: "1.5rem" }}>
                  {String(i + 1).padStart(2, "0")}
                </span>

                {paper.status === "analyzed" ? (
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(paper.id)}
                    onChange={() => toggleSelect(paper.id)}
                  />
                ) : (
                  <span style={{ width: "13px" }} />
                )}

                <Link to={`/papers/${paper.id}`} style={{ flex: 1, color: "var(--ink)" }}>
                  {paper.title || paper.filename}
                </Link>

                <span style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
                  <span className={`status-dot ${paper.status}`} />
                  {paper.status}
                </span>
              </div>
            ))}
          </div>
        )}

        {selectedIds.length > 0 && (
          <div
            style={{
              marginTop: "1.5rem",
              padding: "1rem 1.3rem",
              background: "var(--accent-soft)",
              borderRadius: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <span>{selectedIds.length} paper{selectedIds.length > 1 ? "s" : ""} selected</span>
            <button onClick={handleCompare} disabled={selectedIds.length < 2}>
              Compare selected
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <>
      <TopBar />
      <Routes>
        <Route path="/" element={<PapersList />} />
        <Route path="/papers/:id" element={<PaperDetail />} />
        <Route path="/compare" element={<ComparisonView />} />
      </Routes>
    </>
  );
}

export default App;