import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import api from "./api";
import Spinner from "./Spinner";

const FIELD_LABELS = {
  research_problem: "Research problem",
  method_used: "Method used",
  dataset: "Dataset",
  algorithm: "Algorithm",
  results: "Results",
  advantage: "Advantage",
  limitation: "Limitation",
  future_scope: "Future scope",
};

function ComparisonView() {
  const [searchParams] = useSearchParams();
  const idsParam = searchParams.get("ids");
  const paperIds = idsParam ? idsParam.split(",").map(Number) : [];

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (paperIds.length < 2) { setError("Not enough papers selected."); setLoading(false); return; }
    setLoading(true);
    setError(null);
    api.post("/compare", { paper_ids: paperIds })
      .then((res) => { setData(res.data); setLoading(false); })
      .catch((err) => {
        setError(err.response?.data?.detail || "Comparison failed.");
        setLoading(false);
        console.error(err);
      });
  }, [idsParam]);

  const handleExport = () => {
    api.post("/compare/export", { paper_ids: paperIds }, { responseType: "blob" })
      .then((res) => {
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "comparison_report.xlsx");
        document.body.appendChild(link);
        link.click();
        link.remove();
      })
      .catch((err) => console.error(err));
  };

  return (
    <div className="page wide">
      <Link to="/">← All papers</Link>
      <h1 style={{ marginTop: "1rem" }}>Comparison</h1>

      {loading && <div style={{ marginTop: "2rem" }}><Spinner /><p style={{ color: "var(--muted)" }}>Comparing papers…</p></div>}
      {error && <p style={{ color: "var(--danger)", marginTop: "1rem" }}>{error}</p>}

      {data && (
        <div style={{ marginTop: "1.5rem" }}>
          <button className="secondary" onClick={handleExport} style={{ marginBottom: "1.5rem" }}>
            Export comparison as Excel
          </button>

          <div className="card" style={{ marginBottom: "2rem", background: "var(--accent-soft)", border: "none" }}>
            <p style={{ margin: 0, fontStyle: "italic" }}>{data.comparative_insight}</p>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ minWidth: "600px" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "0.6rem 0", borderBottom: "2px solid var(--ink)" }} />
                  {data.papers_compared.map((p) => (
                    <th key={p.id} style={{ textAlign: "left", padding: "0.6rem 1rem 0.6rem 0", borderBottom: "2px solid var(--ink)", fontFamily: "Newsreader, serif", fontWeight: 500 }}>
                      {p.title}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(FIELD_LABELS).map(([key, label]) => (
                  <tr key={key} style={{ borderBottom: "1px solid var(--line)" }}>
                    <td style={{ padding: "0.75rem 0", verticalAlign: "top" }}>
                      <span className="field-label">{label}</span>
                    </td>
                    {data.papers_compared.map((p) => (
                      <td key={p.id} style={{ padding: "0.75rem 1rem 0.75rem 0", verticalAlign: "top" }}>
                        {data.comparison_table[key]?.[p.title] || "Not specified"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2 style={{ marginTop: "2.5rem" }}>Similarity</h2>
          <div style={{ borderTop: "1px solid var(--line)" }}>
            {data.similarity_scores.map((s, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "0.7rem 0", borderBottom: "1px solid var(--line)", fontSize: "0.92rem" }}>
                <span>{s.paper_a} × {s.paper_b}</span>
                <strong>{s.similarity_score}</strong>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ComparisonView;