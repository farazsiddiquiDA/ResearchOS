import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "./api";

function PaperDetail() {
  const { id } = useParams();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reanalyzing, setReanalyzing] = useState(false);

  const fetchSummary = () => {
    setLoading(true);
    setError(null);
    api.get(`/papers/${id}/summary`)
      .then((response) => {
        setSummary(response.data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.response && err.response.status === 404) {
          setError("No extracted data yet for this paper.");
        } else {
          setError("Failed to load paper summary.");
        }
        setLoading(false);
        console.error(err);
      });
  };

  useEffect(() => {
    fetchSummary();
  }, [id]);

  const handleExport = () => {
    window.open(`http://localhost:8000/papers/${id}/export`, "_blank");
  };

  const handleReanalyze = () => {
    setReanalyzing(true);
    setError(null);
    api.post(`/papers/${id}/analyze`)
      .then(() => {
        return api.get(`/papers/${id}/summary`);
      })
      .then((response) => {
        setSummary(response.data);
        setReanalyzing(false);
      })
      .catch((err) => {
        setError("Re-analysis failed. Try again.");
        setReanalyzing(false);
        console.error(err);
      });
  };

  const fieldRows = summary
    ? [
        ["Research Problem", summary.research_problem],
        ["Method Used", summary.method_used],
        ["Dataset", summary.dataset],
        ["Algorithm", summary.algorithm],
        ["Results", summary.results],
        ["Advantage", summary.advantage],
        ["Limitation", summary.limitation],
        ["Future Scope", summary.future_scope],
      ]
    : [];

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "800px", margin: "0 auto" }}>
      <Link to="/">&larr; Back to all papers</Link>

      {loading && <p>Loading summary...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {summary && (
        <>
          <h1 style={{ fontSize: "2.5rem", lineHeight: "1.3", wordBreak: "break-word" }}>
            {summary.title || summary.filename}
          </h1>

          <div style={{ marginBottom: "1.5rem" }}>
            <button onClick={handleExport} style={{ marginRight: "0.5rem" }}>
              Export as Excel
            </button>
            <button onClick={handleReanalyze} disabled={reanalyzing}>
              {reanalyzing ? "Re-analyzing..." : "Re-analyze"}
            </button>
          </div>

          {summary.narrative_summary && (
            <div style={{ background: "#f5f5f5", padding: "1rem", borderRadius: "8px", marginBottom: "1.5rem" }}>
              <h3>Summary</h3>
              <p>{summary.narrative_summary}</p>
            </div>
          )}

          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              {fieldRows.map(([label, value]) => (
                <tr key={label} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "0.75rem", fontWeight: "bold", verticalAlign: "top", width: "180px" }}>
                    {label}
                  </td>
                  <td style={{ padding: "0.75rem" }}>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

export default PaperDetail;