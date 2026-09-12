function Spinner() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", margin: "0.75rem 0" }}>
      <div style={{
        width: "16px", height: "16px",
        border: "2px solid var(--line)",
        borderTopColor: "var(--accent)",
        borderRadius: "50%",
        animation: "spin 0.7s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export default Spinner;