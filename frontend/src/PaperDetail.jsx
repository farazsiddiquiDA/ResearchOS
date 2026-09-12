import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "./api";
import Spinner from "./Spinner";

function PaperDetail() {
  const { id } = useParams();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reanalyzing, setReanalyzing] = useState(false);
  const [reanalyzeError, setReanalyzeError] = useState(null);

  const fetchSummary = () => {
    setLoading(true);
    setError(null);
    api.get(`/papers/${id}/summary`)
      .then((res) => { setSummary(res.data); setLoading(false); })
      .catch((err) => {
        setError(err.response?.status === 404
          ? "No extracted data yet for this paper."
          : "Couldn't load this summary.");
        setLoading(false);
        console.error(err);
      });
  };

  useEffect(() => { fetchSummary(); }, [id]);

  const handleExport = () => window.open(`http://localhost:8000/papers/${id}/export`, "_blank");

  const handleReanalyze = async () => {
    setReanalyzing(true);
    setReanalyzeError(null);
    try {
      await api.post(`/papers/${id}/analyze`);
      fetchSummary(); // pull the fresh results once re-analysis finishes
    } catch (err) {
      setReanalyzeError("Re-analysis failed. The backend or Groq API may be unavailable — try again shortly.");
      console.error(err);
    } finally {
      setReanalyzing(false);
    }
  };

  const fieldRows = summary ? [
    ["Research problem", summary.research_problem],
    ["Method used", summary.method_used],
    ["Dataset", summary.dataset],
    ["Algorithm", summary.algorithm],
    ["Results", summary.results],
    ["Advantage", summary.advantage],
    ["Limitation", summary.limitation],
    ["Future scope", summary.future_scope],
  ] : [];

  return (
    <div className="page">
      <Link to="/">← All papers</Link>

      {loading && <div style={{ marginTop: "2rem" }}><Spinner /></div>}
      {error && <p style={{ color: "var(--danger)", marginTop: "1rem" }}>{error}</p>}

      {summary && (
        <div style={{ marginTop: "1.5rem" }}>
          <h1>{summary.title || summary.filename}</h1>

          <div style={{ margin: "1.25rem 0", display: "flex", gap: "0.75rem", alignItems: "center" }}>
            <button className="secondary" onClick={handleExport}>Export as Excel</button>
            <button className="secondary" onClick={handleReanalyze} disabled={reanalyzing}>
              {reanalyzing ? "Re-analyzing…" : "Re-analyze"}
            </button>
          </div>

          {reanalyzing && <Spinner />}
          {reanalyzeError && <p style={{ color: "var(--danger)", marginBottom: "1rem" }}>{reanalyzeError}</p>}

          {summary.narrative_summary && (
            <div className="card" style={{ marginBottom: "2rem", background: "var(--accent-soft)", border: "none" }}>
              <p style={{ margin: 0, fontStyle: "italic" }}>{summary.narrative_summary}</p>
            </div>
          )}

          <table>
            <tbody>
              {fieldRows.map(([label, value]) => (
                <tr key={label} style={{ borderBottom: "1px solid var(--line)" }}>
                  <td style={{ padding: "0.9rem 0", width: "180px", verticalAlign: "top" }}>
                    <span className="field-label">{label}</span>
                  </td>
                  <td style={{ padding: "0.9rem 0" }}>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default PaperDetail;