function Spinner() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", margin: "1rem 0" }}>
      <div
        style={{
          width: "18px",
          height: "18px",
          border: "3px solid #ccc",
          borderTopColor: "#2c5282",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default Spinner;