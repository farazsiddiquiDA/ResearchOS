import { useState, useEffect } from "react";
import api from "./api";

function App() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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
  }, []);

  if (loading) return <p>Loading papers...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>ResearchOS</h1>
      <h2>Uploaded Papers</h2>
      {papers.length === 0 ? (
        <p>No papers uploaded yet.</p>
      ) : (
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