import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import api from "./api";
import Spinner from "./Spinner";

const FIELD_LABELS = {
  research_problem: "Research Problem",
  method_used: "Method Used",
  dataset: "Dataset",
  algorithm: "Algorithm",
  results: "Results",
  advantage: "Advantage",
  limitation: "Limitation",
  future_scope: "Future Scope",
};

function ComparisonView() {
  const [searchParams] = useSearchParams();
  const idsParam = searchParams.get("ids");
  const paperIds = idsParam ? idsParam.split(",").map(Number) : [];

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (paperIds.length < 2) {
      setError("Not enough papers selected.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    api.post("/compare", { paper_ids: paperIds })
      .then((response) => {
        setData(response.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Comparison failed.");
        setLoading(false);
        console.error(err);
      });
  }, [idsParam]);

  const handleExport = () => {
    api.post("/compare/export", { paper_ids: paperIds }, { responseType: "blob" })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
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
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "1000px", margin: "0 auto" }}>
      <Link to="/">&larr; Back to all papers</Link>
      <h1>Paper Comparison</h1>

      {loading && (
        <>
          <p>Comparing papers... this may take a moment.</p>
          <Spinner />
        </>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}

      {data && (
        <>
          <button onClick={handleExport} style={{ marginBottom: "1.5rem" }}>
            Export Comparison as Excel
          </button>

          <div style={{ background: "#f5f5f5", padding: "1rem", borderRadius: "8px", marginBottom: "1.5rem" }}>
            <h3>Comparative Insight</h3>
            <p>{data.comparative_insight}</p>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "600px" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "0.5rem", borderBottom: "2px solid #333" }}>Field</th>
                  {data.papers_compared.map((p) => (
                    <th key={p.id} style={{ textAlign: "left", padding: "0.5rem", borderBottom: "2px solid #333" }}>
                      {p.title}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(FIELD_LABELS).map(([fieldKey, fieldLabel]) => (
                  <tr key={fieldKey} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "0.5rem", fontWeight: "bold", verticalAlign: "top" }}>{fieldLabel}</td>
                    {data.papers_compared.map((p) => (
                      <td key={p.id} style={{ padding: "0.5rem", verticalAlign: "top" }}>
                        {data.comparison_table[fieldKey]?.[p.title] || "Not specified"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 style={{ marginTop: "2rem" }}>Similarity Scores</h3>
          <ul>
            {data.similarity_scores.map((s, i) => (
              <li key={i}>
                {s.paper_a} vs {s.paper_b}: <strong>{s.similarity_score}</strong>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default ComparisonView;