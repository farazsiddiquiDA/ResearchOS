import { useState, useEffect } from "react";
import api from "./api";
import UploadForm from "./UploadForm";

function App() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "800px", margin: "0 auto" }}>
      <h1>ResearchOS</h1>

      <UploadForm onUploadComplete={fetchPapers} />

      <h2>Uploaded Papers</h2>
      {loading && <p>Loading papers...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && papers.length === 0 && <p>No papers uploaded yet.</p>}
      {!loading && !error && papers.length > 0 && (
        <ul>
          {papers.map((paper) => (
            <li key={paper.id}>
              <strong>{paper.title || paper.filename}</strong> — {paper.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;