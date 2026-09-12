import { useState } from "react";
import api from "./api";
import Spinner from "./Spinner";

function UploadForm({ onUploadComplete }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 5) {
      setError("Max 5 files at a time.");
      setSelectedFiles([]);
      return;
    }
    setError(null);
    setSelectedFiles(files);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) { setError("Choose at least one PDF."); return; }

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file));

    setUploading(true);
    setError(null);
    setResults(null);

    try {
      const response = await api.post("/papers/process", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResults(response.data.processed);
      setSelectedFiles([]);
      if (onUploadComplete) onUploadComplete();
    } catch (err) {
      setError("Upload failed. Check that the backend is running and try again.");
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h3 style={{ marginBottom: "0.3rem" }}>Add papers</h3>
      <p style={{ color: "var(--muted)", fontSize: "0.9rem", marginTop: 0, marginBottom: "1rem" }}>
        Up to 5 PDFs. Each is read, structured, and analyzed automatically.
      </p>

      <input type="file" accept="application/pdf" multiple onChange={handleFileChange} disabled={uploading} />

      {selectedFiles.length > 0 && (
        <p style={{ fontSize: "0.85rem", color: "var(--muted)", margin: "0.5rem 0" }}>
          {selectedFiles.length} file{selectedFiles.length > 1 ? "s" : ""} ready
        </p>
      )}

      <div style={{ marginTop: "1rem" }}>
        <button onClick={handleUpload} disabled={uploading || selectedFiles.length === 0}>
          {uploading ? "Analyzing…" : "Upload & analyze"}
        </button>
      </div>

      {uploading && <Spinner />}
      {error && <p style={{ color: "var(--danger)", marginTop: "0.75rem" }}>{error}</p>}

      {results && (
        <div style={{ marginTop: "1.25rem", borderTop: "1px solid var(--line)", paddingTop: "1rem" }}>
          {results.map((r, i) => (
            <div key={i} style={{ fontSize: "0.9rem", color: r.error ? "var(--danger)" : "var(--ink)", marginBottom: "0.3rem" }}>
              {r.error ? "· " : "✓ "} {r.filename} {r.error ? `— ${r.error}` : `— ${r.status}`}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default UploadForm;