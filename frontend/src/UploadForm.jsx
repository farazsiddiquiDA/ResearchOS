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
      setError("Max 5 files allowed. Please select fewer files.");
      setSelectedFiles([]);
      return;
    }
    setError(null);
    setSelectedFiles(files);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError("Please select at least one PDF file.");
      return;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

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
    <div style={{ border: "1px solid #ccc", padding: "1.5rem", borderRadius: "8px", marginBottom: "2rem" }}>
      <h2>Upload Papers</h2>
      <p style={{ color: "#666", fontSize: "0.9rem" }}>Select 1–5 PDF files to upload and analyze.</p>

      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={handleFileChange}
        disabled={uploading}
      />

      {selectedFiles.length > 0 && (
        <p>{selectedFiles.length} file(s) selected.</p>
      )}

      <br />

      <button onClick={handleUpload} disabled={uploading || selectedFiles.length === 0}>
        {uploading ? "Processing... (this may take up to a minute)" : "Upload & Analyze"}
      </button>

      {uploading && <Spinner />}

      {error && <p style={{ color: "red" }}>{error}</p>}

      {results && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Results</h3>
          <ul>
            {results.map((r, i) => (
              <li key={i} style={{ color: r.error ? "red" : "green" }}>
                {r.filename}: {r.error ? r.error : `✓ ${r.status}`}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default UploadForm;