import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div
      style={{
        width: "220px",
        background: "#111827",
        color: "white",
        padding: "20px",
        height: "100vh",
      }}
    >
      <h2>Mypedia</h2>

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          marginTop: "40px",
        }}
      >
        <Link to="/">📊 Dashboard</Link>
        <Link to="/news">📰 News</Link>
        <Link to="/notes">📝 Notes</Link>
        <Link to="/chat">💬 Chat</Link>
        <Link to="/trends">📈 Trends</Link>
      </nav>
    </div>
  );
}